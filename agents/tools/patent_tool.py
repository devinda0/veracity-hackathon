"""USPTO patent/trademark research with Playwright fallback for dynamic pages."""

from __future__ import annotations

import asyncio
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import aiohttp

from agents.tools.base import BaseDataSourceTool, ErrorType, ToolResult
from agents.tools.firecrawl_tool import scrape_url
from agents.utils.logger import get_logger

logger = get_logger(__name__)

_PATENT_SEARCH_URL = "https://www.uspto.gov/patents/search"
_TRADEMARK_SEARCH_URL = "https://www.uspto.gov/trademarks/search"
_FILINGS_SEARCH_URL = "https://www.uspto.gov/patents/basics/filing-online"
_BLOCKED_STATUS_CODES = {401, 403, 429}


def _truncate(text: str, limit: int = 240) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen: set[str] = set()
    output: List[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        output.append(item)
    return output


class PatentTool(BaseDataSourceTool):
    """Patent/trademark tool with dynamic-site scraping fallback."""

    def __init__(self) -> None:
        super().__init__(
            name="patent",
            max_retries=2,
            timeout_seconds=45,
            rate_limit=2,
        )
        self._playwright = None
        self._browser = None
        self._context = None
        self._playwright_lock = asyncio.Lock()

    async def _fetch(self, **kwargs: Any) -> Dict[str, Any]:
        search_type = kwargs.get("type", "patent")
        query: str = kwargs["query"]

        if search_type == "patent":
            return await self._search_patents(query)
        if search_type == "trademark":
            return await self._search_trademarks(query)
        if search_type == "filing":
            return await self._search_filings(query)
        raise ValueError(f"Unknown patent search type: {search_type}")

    async def _search_patents(self, query: str) -> Dict[str, Any]:
        url = f"{_PATENT_SEARCH_URL}?q={quote_plus(query)}"
        content_payload = await self._get_uspto_content(url)
        text = content_payload["content"]

        patent_ids = _dedupe_keep_order(
            re.findall(r"\b(US\d{7,12}[A-Z]?\d?)\b", text, flags=re.IGNORECASE)
            + re.findall(r"/patent/(US\d+[A-Z]?\d?)", text, flags=re.IGNORECASE)
        )[:10]

        filing_dates = _dedupe_keep_order(
            re.findall(
                r"(?:filing date|filed)\s*[:\-]?\s*"
                r"(\d{1,2}/\d{1,2}/\d{4}|[A-Za-z]+\s+\d{1,2},\s+\d{4})",
                text,
                flags=re.IGNORECASE,
            )
        )[:10]

        patents = [
            {
                "id": patent_id.upper(),
                "link": f"https://patents.google.com/?q={quote_plus(patent_id)}",
                "source": "uspto",
            }
            for patent_id in patent_ids
        ]

        filings = [
            {
                "type": "patent_filing",
                "date": filing_date,
                "source": "uspto",
            }
            for filing_date in filing_dates
        ]

        return {
            "query": query,
            "patents": patents,
            "filings": filings,
            "source": "uspto_patents",
            "content_source": content_payload["source"],
        }

    async def _search_trademarks(self, query: str) -> Dict[str, Any]:
        url = f"{_TRADEMARK_SEARCH_URL}?q={quote_plus(query)}"
        content_payload = await self._get_uspto_content(url)
        text = content_payload["content"]

        serial_numbers = _dedupe_keep_order(
            re.findall(r"\bserial(?:\s+number)?\s*[:#]?\s*(\d{7,8})\b", text, flags=re.IGNORECASE)
        )[:10]
        registration_numbers = _dedupe_keep_order(
            re.findall(
                r"\bregistration(?:\s+number)?\s*[:#]?\s*(\d{6,8})\b",
                text,
                flags=re.IGNORECASE,
            )
        )[:10]
        filing_dates = _dedupe_keep_order(
            re.findall(
                r"(?:filing date|filed)\s*[:\-]?\s*"
                r"(\d{1,2}/\d{1,2}/\d{4}|[A-Za-z]+\s+\d{1,2},\s+\d{4})",
                text,
                flags=re.IGNORECASE,
            )
        )[:10]

        trademarks = [
            {
                "serial_number": serial,
                "registration_number": registration_numbers[idx] if idx < len(registration_numbers) else None,
                "source": "uspto",
            }
            for idx, serial in enumerate(serial_numbers)
        ]

        filings = [
            {
                "type": "trademark_filing",
                "date": filing_date,
                "source": "uspto",
            }
            for filing_date in filing_dates
        ]

        return {
            "query": query,
            "trademarks": trademarks,
            "filings": filings,
            "source": "uspto_trademarks",
            "content_source": content_payload["source"],
        }

    async def _search_filings(self, query: str) -> Dict[str, Any]:
        # USPTO filing guidance often serves dynamic content and is a good
        # candidate for the Firecrawl -> Playwright fallback flow.
        url = f"{_FILINGS_SEARCH_URL}?q={quote_plus(query)}"
        content_payload = await self._get_uspto_content(url)
        text = content_payload["content"]

        filing_refs = _dedupe_keep_order(
            re.findall(
                r"\b(?:application\s+number|filing\s+number|serial\s+number)\s*[:#]?\s*([A-Z0-9\-/]{6,20})\b",
                text,
                flags=re.IGNORECASE,
            )
        )[:15]

        filing_dates = _dedupe_keep_order(
            re.findall(
                r"(?:filing date|filed)\s*[:\-]?\s*"
                r"(\d{1,2}/\d{1,2}/\d{4}|[A-Za-z]+\s+\d{1,2},\s+\d{4})",
                text,
                flags=re.IGNORECASE,
            )
        )[:15]

        filings = [
            {
                "reference": filing_refs[idx] if idx < len(filing_refs) else None,
                "date": filing_dates[idx] if idx < len(filing_dates) else None,
                "source": "uspto",
            }
            for idx in range(max(len(filing_refs), len(filing_dates)))
        ]

        return {
            "query": query,
            "filings": [row for row in filings if row.get("reference") or row.get("date")],
            "source": "uspto_filings",
            "content_source": content_payload["source"],
        }

    async def _get_uspto_content(self, url: str) -> Dict[str, str]:
        """Get content with Firecrawl first, then Playwright on rate limits."""
        firecrawl_result = await scrape_url(url)
        if firecrawl_result.success and firecrawl_result.data:
            return {
                "content": firecrawl_result.data.get("content", ""),
                "source": "firecrawl",
            }

        if firecrawl_result.error_type == ErrorType.RATE_LIMIT:
            logger.warning("firecrawl_rate_limited_fallback_playwright", url=url)
            content = await self._scrape_with_playwright(url)
            return {"content": content, "source": "playwright_fallback"}

        # If Firecrawl fails for any other reason, fall back to plain HTTP.
        logger.warning(
            "firecrawl_fallback_http",
            url=url,
            error=firecrawl_result.error,
            error_type=str(firecrawl_result.error_type),
        )
        content = await self._fetch_with_http(url)
        return {"content": content, "source": "http_fallback"}

    async def _fetch_with_http(self, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=self.timeout_seconds),
            ) as resp:
                if resp.status in _BLOCKED_STATUS_CODES:
                    raise Exception(f"blocked request from USPTO page: HTTP {resp.status}")
                if resp.status != 200:
                    raise Exception(f"USPTO error: HTTP {resp.status}")
                return await resp.text()

    async def _ensure_playwright_session(self) -> None:
        if self._playwright and self._browser and self._context:
            return

        async with self._playwright_lock:
            if self._playwright and self._browser and self._context:
                return

            from playwright.async_api import async_playwright  # type: ignore[import]

            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True)
            self._context = await self._browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                )
            )
            logger.info("playwright_session_cached", tool=self.name)

    async def _scrape_with_playwright(self, url: str) -> str:
        try:
            from playwright.async_api import TimeoutError as PlaywrightTimeoutError  # type: ignore[import]
        except Exception as exc:
            raise Exception("validation: Playwright is required for dynamic-site fallback") from exc

        await self._ensure_playwright_session()
        page = await self._context.new_page()

        try:
            await page.goto(
                url,
                timeout=self.timeout_seconds * 1000,
                wait_until="domcontentloaded",
            )
            content = await page.content()
            lowered = content.lower()
            if "captcha" in lowered or "access denied" in lowered or "verify you are human" in lowered:
                raise Exception("blocked request from dynamic page")
            return _truncate(content, limit=20000)
        except PlaywrightTimeoutError as exc:
            raise Exception("dynamic page timeout while scraping") from exc
        finally:
            await page.close()

    async def close(self) -> None:
        """Gracefully close cached Playwright session resources."""
        async with self._playwright_lock:
            if self._context is not None:
                await self._context.close()
                self._context = None
            if self._browser is not None:
                await self._browser.close()
                self._browser = None
            if self._playwright is not None:
                await self._playwright.stop()
                self._playwright = None


_patent = PatentTool()


async def search_patents(query: str) -> ToolResult:
    """Search USPTO patent-related content and parse patent identifiers."""
    return await _patent.execute(type="patent", query=query)


async def search_trademarks(query: str) -> ToolResult:
    """Search USPTO trademark-related content and parse trademark identifiers."""
    return await _patent.execute(type="trademark", query=query)


async def search_filings(query: str) -> ToolResult:
    """Search USPTO filing-related content and parse filing references."""
    return await _patent.execute(type="filing", query=query)
