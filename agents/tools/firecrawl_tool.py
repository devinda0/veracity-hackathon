"""Firecrawl wrapper for web scraping and search."""

import os
from typing import Any, Dict

import aiohttp

from agents.tools.base import BaseDataSourceTool, ToolResult
from agents.utils.logger import get_logger

logger = get_logger(__name__)

_FIRECRAWL_BASE_URL = "https://api.firecrawl.dev/v1"


class FirecrawlTool(BaseDataSourceTool):
    """Firecrawl API client with async support, retry, and rate limiting."""

    def __init__(self) -> None:
        super().__init__(
            name="firecrawl",
            max_retries=3,
            timeout_seconds=30,
            rate_limit=5,
        )
        self.api_key: str = os.environ.get("FIRECRAWL_API_KEY", "")
        self.base_url: str = _FIRECRAWL_BASE_URL

    async def _fetch(self, **kwargs: Any) -> Dict[str, Any]:
        """Dispatch to scrape or search based on the 'action' kwarg."""
        action: str = kwargs.get("action", "scrape")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        if action == "scrape":
            url: str = kwargs["url"]
            return await self._scrape_url(url, headers)
        elif action == "search":
            query: str = kwargs["query"]
            return await self._search(query, headers)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def _scrape_url(self, url: str, headers: dict) -> Dict[str, Any]:
        """Fetch a URL and return its markdown content."""
        async with aiohttp.ClientSession() as session:
            payload = {
                "url": url,
                "formats": ["markdown"],
            }
            async with session.post(
                f"{self.base_url}/scrape",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout_seconds),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Firecrawl v1 wraps content in a nested "data" key
                    inner = data.get("data") or data
                    return {
                        "url": url,
                        "content": inner.get("markdown", ""),
                        "source": "firecrawl",
                    }
                elif resp.status == 429:
                    raise Exception("rate limit exceeded by Firecrawl")
                else:
                    raise Exception(f"Firecrawl scrape error: HTTP {resp.status}")

    async def _search(self, query: str, headers: dict) -> Dict[str, Any]:
        """Run a web search and return up to 10 results with snippets."""
        async with aiohttp.ClientSession() as session:
            payload = {
                "query": query,
                "limit": 10,
            }
            async with session.post(
                f"{self.base_url}/search",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout_seconds),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Firecrawl v1 returns search results under "data", not "results"
                    results = data.get("data") or data.get("results", [])
                    return {
                        "query": query,
                        "results": results,
                        "source": "firecrawl",
                    }
                elif resp.status == 429:
                    raise Exception("rate limit exceeded by Firecrawl")
                else:
                    raise Exception(f"Firecrawl search error: HTTP {resp.status}")


# ---------------------------------------------------------------------------
# Module-level singleton and convenience helpers
# ---------------------------------------------------------------------------

_firecrawl: FirecrawlTool = FirecrawlTool()


async def scrape_url(url: str) -> ToolResult:
    """Scrape a URL and return its markdown content."""
    return await _firecrawl.execute(action="scrape", url=url)


async def search_web(query: str) -> ToolResult:
    """Search the web and return top 10 results with snippets."""
    return await _firecrawl.execute(action="search", query=query)
