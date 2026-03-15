"""Community data source wrapper for Reddit and Hacker News."""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import aiohttp

from agents.tools.base import BaseDataSourceTool, ToolResult
from agents.utils.logger import get_logger

logger = get_logger(__name__)

_HN_ALGOLIA_URL = "https://hn.algolia.com/api/v1/search"
_DEFAULT_SUBREDDITS = ["startup", "business", "entrepreneur", "technology"]

_POSITIVE_TERMS = {
    "great",
    "good",
    "excellent",
    "love",
    "promising",
    "growth",
    "opportunity",
    "success",
    "improve",
    "innovative",
}
_NEGATIVE_TERMS = {
    "bad",
    "poor",
    "decline",
    "risk",
    "problem",
    "issue",
    "fail",
    "failure",
    "concern",
    "expensive",
}


def _sentiment_label(text: str) -> str:
    """Very light-weight lexical sentiment label."""
    lowered = (text or "").lower()
    positive_hits = sum(1 for term in _POSITIVE_TERMS if term in lowered)
    negative_hits = sum(1 for term in _NEGATIVE_TERMS if term in lowered)
    if positive_hits > negative_hits:
        return "positive"
    if negative_hits > positive_hits:
        return "negative"
    return "neutral"


class CommunityTool(BaseDataSourceTool):
    """Community insights via Reddit and Hacker News."""

    def __init__(self) -> None:
        super().__init__(
            name="community",
            max_retries=2,
            timeout_seconds=20,
            rate_limit=5,
        )
        self.reddit_client_id = os.environ.get("REDDIT_CLIENT_ID", "")
        self.reddit_client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
        self.reddit_user_agent = "vector-agents/1.0"
        self._hn_url = _HN_ALGOLIA_URL

        # Deferred import keeps editor diagnostics clean when deps are not yet installed.
        import praw  # type: ignore[import]

        self.reddit = praw.Reddit(
            client_id=self.reddit_client_id,
            client_secret=self.reddit_client_secret,
            user_agent=self.reddit_user_agent,
        )

    async def _fetch(self, **kwargs: Any) -> Dict[str, Any]:
        source = kwargs.get("source", "reddit")
        query: str = kwargs["query"]
        limit = int(kwargs.get("limit", 25))
        max_age_days = int(kwargs.get("max_age_days", 30))
        min_score = int(kwargs.get("min_score", 0))
        min_engagement = int(kwargs.get("min_engagement", 0))

        if source == "reddit":
            return await self._search_reddit(
                query=query,
                limit=limit,
                max_age_days=max_age_days,
                min_score=min_score,
                min_engagement=min_engagement,
            )
        if source == "hackernews":
            return await self._search_hackernews(
                query=query,
                limit=limit,
                max_age_days=max_age_days,
                min_score=min_score,
                min_engagement=min_engagement,
            )
        raise ValueError(f"Unknown source: {source}")

    async def _search_reddit(
        self,
        query: str,
        limit: int,
        max_age_days: int,
        min_score: int,
        min_engagement: int,
    ) -> Dict[str, Any]:
        return await asyncio.to_thread(
            self._search_reddit_sync,
            query,
            limit,
            max_age_days,
            min_score,
            min_engagement,
        )

    def _search_reddit_sync(
        self,
        query: str,
        limit: int,
        max_age_days: int,
        min_score: int,
        min_engagement: int,
    ) -> Dict[str, Any]:
        if not self.reddit_client_id or not self.reddit_client_secret:
            raise ValueError("validation: missing REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET")

        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        posts: List[Dict[str, Any]] = []
        per_subreddit_limit = max(5, min(15, limit))

        for subreddit_name in _DEFAULT_SUBREDDITS:
            subreddit = self.reddit.subreddit(subreddit_name)
            for post in subreddit.search(
                query,
                time_filter="month",
                sort="relevance",
                limit=per_subreddit_limit,
            ):
                created_dt = datetime.fromtimestamp(float(post.created_utc), tz=timezone.utc)
                if created_dt < cutoff:
                    continue

                score = int(getattr(post, "score", 0) or 0)
                num_comments = int(getattr(post, "num_comments", 0) or 0)
                engagement = score + num_comments
                if score < min_score or engagement < min_engagement:
                    continue

                top_comments: List[Dict[str, Any]] = []
                try:
                    post.comment_sort = "top"
                    post.comments.replace_more(limit=0)
                    for comment in post.comments[:3]:
                        body = str(getattr(comment, "body", "") or "")
                        top_comments.append(
                            {
                                "body": body,
                                "score": int(getattr(comment, "score", 0) or 0),
                                "sentiment": _sentiment_label(body),
                            }
                        )
                except Exception as comment_exc:
                    logger.warning(
                        "reddit_comment_parse_failed",
                        subreddit=subreddit_name,
                        error=str(comment_exc),
                    )

                text_blob = f"{getattr(post, 'title', '')} {getattr(post, 'selftext', '')}"
                posts.append(
                    {
                        "title": str(getattr(post, "title", "") or ""),
                        "subreddit": subreddit_name,
                        "score": score,
                        "num_comments": num_comments,
                        "engagement": engagement,
                        "url": str(getattr(post, "url", "") or ""),
                        "created": created_dt.isoformat(),
                        "sentiment": _sentiment_label(text_blob),
                        "top_comments": top_comments,
                    }
                )

        posts.sort(key=lambda item: item.get("engagement", 0), reverse=True)
        return {
            "query": query,
            "posts": posts[:limit],
            "source": "reddit",
            "filters": {
                "max_age_days": max_age_days,
                "min_score": min_score,
                "min_engagement": min_engagement,
            },
        }

    async def _search_hackernews(
        self,
        query: str,
        limit: int,
        max_age_days: int,
        min_score: int,
        min_engagement: int,
    ) -> Dict[str, Any]:
        cutoff_ts = int((datetime.now(timezone.utc) - timedelta(days=max_age_days)).timestamp())
        params = {
            "query": query,
            "tags": "story",
            "hitsPerPage": max(limit * 2, limit),
            "numericFilters": f"created_at_i>{cutoff_ts}",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                self._hn_url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=self.timeout_seconds),
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"HN Algolia error: HTTP {resp.status}")

                data = await resp.json()
                stories: List[Dict[str, Any]] = []
                for hit in data.get("hits", []):
                    points = int(hit.get("points") or 0)
                    num_comments = int(hit.get("num_comments") or 0)
                    engagement = points + num_comments
                    if points < min_score or engagement < min_engagement:
                        continue

                    title = hit.get("title") or hit.get("story_title") or ""
                    stories.append(
                        {
                            "title": title,
                            "url": hit.get("url") or hit.get("story_url"),
                            "points": points,
                            "num_comments": num_comments,
                            "engagement": engagement,
                            "created_at": hit.get("created_at"),
                            "sentiment": _sentiment_label(str(title)),
                        }
                    )

                stories.sort(key=lambda item: item.get("engagement", 0), reverse=True)
                return {
                    "query": query,
                    "stories": stories[:limit],
                    "source": "hackernews",
                    "filters": {
                        "max_age_days": max_age_days,
                        "min_score": min_score,
                        "min_engagement": min_engagement,
                    },
                }


_community = CommunityTool()


async def search_reddit(
    query: str,
    limit: int = 25,
    max_age_days: int = 30,
    min_score: int = 0,
    min_engagement: int = 0,
) -> ToolResult:
    """Search Reddit posts and comments for community insights."""
    return await _community.execute(
        source="reddit",
        query=query,
        limit=limit,
        max_age_days=max_age_days,
        min_score=min_score,
        min_engagement=min_engagement,
    )


async def search_hackernews(
    query: str,
    limit: int = 25,
    max_age_days: int = 30,
    min_score: int = 0,
    min_engagement: int = 0,
) -> ToolResult:
    """Search Hacker News via Algolia for recent stories."""
    return await _community.execute(
        source="hackernews",
        query=query,
        limit=limit,
        max_age_days=max_age_days,
        min_score=min_score,
        min_engagement=min_engagement,
    )
