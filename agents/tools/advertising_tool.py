"""Advertising intelligence tool for Meta Ad Library and LinkedIn."""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import aiohttp

from agents.tools.base import BaseDataSourceTool, ToolResult
from agents.utils.logger import get_logger

logger = get_logger(__name__)

_META_ADS_URL = "https://ads.facebook.com/ads/library/api"
_DEFAULT_CACHE_TTL = timedelta(hours=6)
_BLOCKED_HTTP_STATUSES = {401, 403, 999}


def _slugify_company(value: str) -> str:
    lowered = value.strip().lower()
    normalized = re.sub(r"[^a-z0-9\-\s]", "", lowered)
    return re.sub(r"\s+", "-", normalized).strip("-")


class AdvertisingTool(BaseDataSourceTool):
    """Competitive advertising intelligence via Meta and LinkedIn."""

    def __init__(self) -> None:
        super().__init__(
            name="advertising",
            max_retries=2,
            timeout_seconds=30,
            rate_limit=3,
        )
        self.meta_access_token = os.environ.get("META_AD_LIBRARY_ACCESS_TOKEN", "")
        self._cache: Dict[str, tuple[datetime, Dict[str, Any]]] = {}
        self._cache_ttl = _DEFAULT_CACHE_TTL

    async def _fetch(self, **kwargs: Any) -> Dict[str, Any]:
        source = kwargs.get("source", "meta")
        query: str = kwargs["query"]

        cache_key = f"{source}:{query.strip().lower()}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            cached["cached"] = True
            return cached

        if source == "meta":
            payload = await self._search_meta_ads(query)
        elif source == "linkedin":
            payload = await self._search_linkedin(query)
        else:
            raise ValueError(f"Unknown advertising source: {source}")

        payload["cached"] = False
        self._set_cached(cache_key, payload)
        return payload

    def _get_cached(self, key: str) -> Optional[Dict[str, Any]]:
        entry = self._cache.get(key)
        if not entry:
            return None

        created_at, value = entry
        if datetime.now(timezone.utc) - created_at > self._cache_ttl:
            self._cache.pop(key, None)
            return None

        return dict(value)

    def _set_cached(self, key: str, value: Dict[str, Any]) -> None:
        self._cache[key] = (datetime.now(timezone.utc), dict(value))

    async def _search_meta_ads(self, company_name: str) -> Dict[str, Any]:
        """Fetch ad data from Meta Ad Library endpoint."""
        params = {
            "search_term": company_name,
            "ad_type": "ALL",
            "country": "US",
        }
        if self.meta_access_token:
            params["access_token"] = self.meta_access_token

        async with aiohttp.ClientSession() as session:
            async with session.get(
                _META_ADS_URL,
                params=params,
                timeout=aiohttp.ClientTimeout(total=self.timeout_seconds),
            ) as resp:
                if resp.status == 429:
                    raise Exception("rate limit exceeded by Meta Ad Library")
                if resp.status in _BLOCKED_HTTP_STATUSES:
                    raise Exception(f"blocked request by Meta Ad Library: HTTP {resp.status}")
                if resp.status != 200:
                    raise Exception(f"Meta API error: HTTP {resp.status}")

                data = await resp.json()
                return {
                    "company": company_name,
                    "ads": self._parse_meta_ads(data),
                    "source": "meta_ad_library",
                }

    def _parse_meta_ads(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize Meta ad payload into ad copy, targeting, and creatives."""
        ads: List[Dict[str, Any]] = []
        for ad in (data.get("ads") or data.get("data") or [])[:20]:
            bodies = ad.get("ad_creative_bodies") or []
            body_text = ""
            if bodies:
                first_body = bodies[0]
                if isinstance(first_body, dict):
                    body_text = str(first_body.get("body", ""))
                else:
                    body_text = str(first_body)

            creative_assets = {
                "images": ad.get("ad_creative_link_captions") or ad.get("images") or [],
                "videos": ad.get("ad_creative_link_titles") or ad.get("videos") or [],
                "snapshot_url": ad.get("ad_snapshot_url"),
            }
            targeting = {
                "countries": ad.get("target_locations") or ad.get("delivery_by_region") or [],
                "demographics": ad.get("demographic_distribution") or [],
                "age": ad.get("age_country_gender_reach_breakdown") or [],
            }

            ads.append(
                {
                    "ad_copy": body_text,
                    "targeting": targeting,
                    "creatives": creative_assets,
                    "created_date": ad.get("ad_creation_time") or ad.get("ad_creation_date"),
                    "impressions": ad.get("impressions"),
                    "spend": ad.get("spend"),
                    "status": ad.get("ad_delivery_status"),
                }
            )

        return ads

    async def _search_linkedin(self, company_name: str) -> Dict[str, Any]:
        """Scrape public LinkedIn company pages via Playwright."""
        slug = _slugify_company(company_name)
        company_url = (
            company_name
            if company_name.startswith("http://") or company_name.startswith("https://")
            else f"https://www.linkedin.com/company/{slug}/"
        )

        try:
            from playwright.async_api import TimeoutError as PlaywrightTimeoutError  # type: ignore[import]
            from playwright.async_api import async_playwright  # type: ignore[import]
        except Exception as exc:
            raise Exception("validation: Playwright is required for LinkedIn scraping") from exc

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/122.0.0.0 Safari/537.36"
                    )
                )
                page = await context.new_page()

                await page.goto(
                    company_url,
                    timeout=self.timeout_seconds * 1000,
                    wait_until="domcontentloaded",
                )

                page_text = (await page.content()).lower()
                if "captcha" in page_text or "security verification" in page_text:
                    raise Exception("blocked request by LinkedIn: captcha/security challenge")

                company_info = await page.evaluate(
                    """
                    () => {
                      const pickText = (selectors) => {
                        for (const sel of selectors) {
                          const el = document.querySelector(sel);
                          if (el && el.textContent) {
                            const value = el.textContent.trim();
                            if (value) return value;
                          }
                        }
                        return "";
                      };

                      const headerText = Array.from(document.querySelectorAll("span, div"))
                        .map((el) => (el.textContent || "").trim())
                        .find((t) => /employees/i.test(t)) || "";

                      return {
                        name: pickText(["h1", ".top-card-layout__title", ".org-top-card-summary__title"]),
                        tagline: pickText([".top-card-layout__headline", ".org-top-card-summary__tagline", "p"]),
                        about: pickText(["section p", ".core-section-container__content p", ".break-words"]),
                        employees_text: headerText,
                      };
                    }
                    """
                )

                jobs_url = company_url.rstrip("/") + "/jobs/"
                await page.goto(
                    jobs_url,
                    timeout=self.timeout_seconds * 1000,
                    wait_until="domcontentloaded",
                )
                jobs = await page.evaluate(
                    """
                    () => {
                      const links = Array.from(document.querySelectorAll('a[href*="/jobs/view/"]'));
                      const seen = new Set();
                      const results = [];
                      for (const link of links) {
                        const title = (link.textContent || "").trim();
                        const url = link.href;
                        if (!title || !url || seen.has(url)) continue;
                        seen.add(url);
                        results.push({ title, url });
                        if (results.length >= 10) break;
                      }
                      return results;
                    }
                    """
                )

                await context.close()
                await browser.close()

        except PlaywrightTimeoutError as exc:
            raise Exception("LinkedIn request timeout") from exc

        employees_count = None
        employees_text = company_info.get("employees_text") or ""
        match = re.search(r"([\d,]+)\+?\s+employees", employees_text, flags=re.IGNORECASE)
        if match:
            employees_count = int(match.group(1).replace(",", ""))

        return {
            "company": company_name,
            "company_url": company_url,
            "company_info": {
                "name": company_info.get("name"),
                "tagline": company_info.get("tagline"),
                "about": company_info.get("about"),
                "employees_count": employees_count,
            },
            "employees": [] if employees_count is None else [{"count": employees_count}],
            "job_postings": jobs,
            "source": "linkedin",
        }


_advertising = AdvertisingTool()


async def search_meta_ads(company_name: str) -> ToolResult:
    """Search Meta Ad Library for a target company."""
    return await _advertising.execute(source="meta", query=company_name)


async def search_linkedin(company_name: str) -> ToolResult:
    """Scrape a LinkedIn company profile for company and jobs insights."""
    return await _advertising.execute(source="linkedin", query=company_name)
