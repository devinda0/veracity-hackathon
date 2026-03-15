"""SerpAPI wrapper for Google Search, Trends, and News."""

import os
from typing import Any, Dict

import aiohttp

from agents.tools.base import BaseDataSourceTool, ToolResult
from agents.utils.logger import get_logger

logger = get_logger(__name__)

_SERPAPI_BASE_URL = "https://serpapi.com/search"


class SerpAPITool(BaseDataSourceTool):
    """SerpAPI client with async support, retry, and conservative rate limiting."""

    def __init__(self) -> None:
        super().__init__(
            name="serpapi",
            max_retries=2,
            timeout_seconds=30,
            rate_limit=3,  # Conservative — SerpAPI free tier: 100 calls/month
        )
        self.api_key: str = os.environ.get("SERPAPI_API_KEY", "")
        self.base_url: str = _SERPAPI_BASE_URL

    async def _fetch(self, **kwargs: Any) -> Dict[str, Any]:
        """Dispatch a SerpAPI GET request based on 'type' kwarg."""
        search_type: str = kwargs.get("type", "google")
        query: str = kwargs["query"]

        params: Dict[str, Any] = {
            "api_key": self.api_key,
            "q": query,
        }

        if search_type == "google":
            params["engine"] = "google"
            params["num"] = 10
        elif search_type == "trends":
            params["engine"] = "google_trends"
            params["data_type"] = "TIMESERIES"
        elif search_type == "news":
            params["engine"] = "google_news"
            params["num"] = 10
        else:
            raise ValueError(f"Unknown search type: {search_type}")

        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.base_url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=self.timeout_seconds),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return self._parse_response(search_type, data)
                elif resp.status == 429:
                    raise Exception("rate limit exceeded by SerpAPI")
                else:
                    raise Exception(f"SerpAPI error: HTTP {resp.status}")

    def _parse_response(self, search_type: str, data: dict) -> Dict[str, Any]:
        """Normalise raw SerpAPI response into a consistent structure."""
        query = data.get("search_parameters", {}).get("q")

        if search_type == "google":
            return {
                "query": query,
                "results": [
                    {
                        "title": r.get("title"),
                        "link": r.get("link"),
                        "snippet": r.get("snippet"),
                    }
                    for r in data.get("organic_results", [])[:10]
                ],
                "source": "serpapi",
            }
        elif search_type == "trends":
            return {
                "query": query,
                "interest_over_time": data.get("interest_over_time", []),
                "related_queries": data.get("related_queries", []),
                "source": "serpapi_trends",
            }
        elif search_type == "news":
            return {
                "query": query,
                "news": [
                    {
                        "title": n.get("title"),
                        "source": n.get("source"),
                        "date": n.get("date"),
                        "link": n.get("link"),
                    }
                    for n in data.get("news_results", [])[:10]
                ],
                "source": "serpapi_news",
            }
        else:
            # Should never reach here; _fetch validates search_type first.
            return {"query": query, "raw": data, "source": "serpapi"}


# ---------------------------------------------------------------------------
# Module-level singleton and convenience helpers
# ---------------------------------------------------------------------------

_serpapi: SerpAPITool = SerpAPITool()


async def google_search(query: str) -> ToolResult:
    """Return organic Google search results for a query."""
    return await _serpapi.execute(type="google", query=query)


async def google_trends(query: str) -> ToolResult:
    """Return Google Trends interest-over-time data for a query."""
    return await _serpapi.execute(type="trends", query=query)


async def google_news(query: str) -> ToolResult:
    """Return recent Google News results for a query."""
    return await _serpapi.execute(type="news", query=query)
