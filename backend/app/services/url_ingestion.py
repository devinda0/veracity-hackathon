from __future__ import annotations

import asyncio
import hashlib
import re
import sys
from datetime import UTC, datetime, timedelta
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import aiohttp
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import HttpUrl, TypeAdapter, ValidationError

from app.core.logger import get_logger
from app.services.document_parser import DocumentParser

logger = get_logger(__name__)
_URL_ADAPTER = TypeAdapter(HttpUrl)
_REPO_ROOT = Path(__file__).resolve().parents[3]


class URLIngestionError(Exception):
    """Raised when a URL cannot be ingested."""


class URLIngestionService:
    """Ingest URLs through Firecrawl with Playwright fallback and Mongo caching."""

    cache_ttl = timedelta(days=7)
    timeout_seconds = 45

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db

    async def ingest_url(self, url: str, session_id: str, user_id: str) -> dict[str, Any]:
        normalized_url = self._normalize_url(url)
        url_hash = self._url_hash(normalized_url)

        cached = await self._get_cached_result(url_hash)
        if cached is not None:
            logger.info("url_cache_hit", url=normalized_url, session_id=session_id, user_id=user_id)
            return {
                "url": normalized_url,
                "url_hash": url_hash,
                "content": cached["content"],
                "chunks": cached["chunks"],
                "source": "cache",
                "method": cached.get("method", "cache"),
                "cached": True,
            }

        async with asyncio.timeout(self.timeout_seconds):
            content, method = await self._fetch_content(normalized_url)

        chunks = DocumentParser.chunk_text(content)
        if not chunks:
            raise URLIngestionError("No readable content could be extracted from the URL")

        cache_doc = {
            "url": normalized_url,
            "url_hash": url_hash,
            "content": content,
            "chunks": chunks,
            "method": method,
            "created_at": datetime.now(UTC),
        }
        await self.db.url_cache.update_one(
            {"url_hash": url_hash},
            {"$set": cache_doc},
            upsert=True,
        )

        logger.info(
            "url_ingested",
            url=normalized_url,
            session_id=session_id,
            user_id=user_id,
            method=method,
            chunks=len(chunks),
        )
        return {
            "url": normalized_url,
            "url_hash": url_hash,
            "content": content,
            "chunks": chunks,
            "source": "web",
            "method": method,
            "cached": False,
        }

    @classmethod
    def _normalize_url(cls, url: str) -> str:
        try:
            validated = str(_URL_ADAPTER.validate_python(url))
        except ValidationError as exc:
            raise URLIngestionError("Invalid URL") from exc

        parts = urlsplit(validated)
        normalized_path = parts.path or "/"
        if normalized_path != "/":
            normalized_path = normalized_path.rstrip("/")
            normalized_path = normalized_path or "/"

        return urlunsplit(
            (
                parts.scheme.lower(),
                parts.netloc.lower(),
                normalized_path,
                parts.query,
                "",
            )
        )

    @staticmethod
    def _url_hash(url: str) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    async def _get_cached_result(self, url_hash: str) -> dict[str, Any] | None:
        cached = await self.db.url_cache.find_one({"url_hash": url_hash})
        if cached is None:
            return None

        created_at = cached.get("created_at")
        if not isinstance(created_at, datetime):
            return None

        if self._ensure_utc(created_at) + self.cache_ttl <= datetime.now(UTC):
            return None

        return cached

    async def _fetch_content(self, url: str) -> tuple[str, str]:
        try:
            content = await self._fetch_with_firecrawl(url)
            return content, "firecrawl"
        except Exception as exc:
            logger.warning("firecrawl_fetch_failed", url=url, error=str(exc))

        try:
            content = await self._fetch_with_playwright(url)
            return content, "playwright"
        except Exception as exc:
            logger.warning("playwright_fetch_failed", url=url, error=str(exc))

        content = await self._fetch_with_http(url)
        return content, "http"

    async def _fetch_with_firecrawl(self, url: str) -> str:
        if str(_REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(_REPO_ROOT))

        from agents.tools.firecrawl_tool import scrape_url

        result = await scrape_url(url)
        if not result.success:
            raise URLIngestionError(result.error or "Firecrawl request failed")

        data = result.data or {}
        content = self._clean_content(str(data.get("content", "")))
        if not content:
            raise URLIngestionError("Firecrawl returned empty content")
        return content

    async def _fetch_with_playwright(self, url: str) -> str:
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError
        from playwright.async_api import async_playwright

        try:
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=True)
                page = await browser.new_page()
                try:
                    await page.goto(url, wait_until="networkidle", timeout=self.timeout_seconds * 1000)
                    text = await page.locator("body").inner_text(timeout=10_000)
                finally:
                    await browser.close()
        except PlaywrightTimeoutError as exc:
            raise URLIngestionError("Playwright timed out") from exc
        except Exception as exc:
            raise URLIngestionError(f"Playwright fetch failed: {exc}") from exc

        content = self._clean_content(text)
        if not content:
            raise URLIngestionError("Playwright returned empty content")
        return content

    async def _fetch_with_http(self, url: str) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout_seconds),
                    allow_redirects=True,
                    headers={"User-Agent": "VectorAgentsBot/1.0"},
                ) as response:
                    if response.status != 200:
                        raise URLIngestionError(f"HTTP fetch failed with status {response.status}")
                    html = await response.text()
        except asyncio.TimeoutError as exc:
            raise URLIngestionError("HTTP fetch timed out") from exc
        except aiohttp.ClientError as exc:
            raise URLIngestionError(f"HTTP fetch failed: {exc}") from exc

        content = self._extract_text_from_html(html)
        if not content:
            raise URLIngestionError("HTTP fallback returned empty content")
        return content

    @classmethod
    def _clean_content(cls, content: str) -> str:
        return DocumentParser._normalize_text(content)

    @classmethod
    def _extract_text_from_html(cls, html: str) -> str:
        text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html)
        text = re.sub(r"(?s)<[^>]+>", " ", text)
        return cls._clean_content(unescape(text))

    @staticmethod
    def _ensure_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
