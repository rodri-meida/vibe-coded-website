"""Service layer for fetching trending repositories from the GitHub API."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class GitHubServiceError(Exception):
    """Custom exception for GitHub service errors."""
    pass


class GitHubService:
    """Wrapper around the GitHub Search API for trending repositories."""

    def __init__(self):
        self.base_url = getattr(settings, "GITHUB_API_BASE_URL", "https://api.github.com")
        self.token = getattr(settings, "GITHUB_TOKEN", None)
        self.timeout = 15
        self.per_page = getattr(settings, "REPOS_PER_PAGE", 30)

    def _headers(self) -> dict:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "GitHub-Trending-Django/1.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _build_cache_key(self, language: str, period: str, search: str, sort: str) -> str:
        return f"github:trending:{language}:{period}:{search}:{sort}"

    def _get_period_date(self, period: str) -> Optional[str]:
        """Build the date qualifier based on the period."""
        now = datetime.now(timezone.utc)
        if period == "weekly":
            return (now - timedelta(days=7)).strftime("%Y-%m-%d")
        elif period == "monthly":
            return (now - timedelta(days=30)).strftime("%Y-%m-%d")
        elif period == "yearly":
            return (now - timedelta(days=365)).strftime("%Y-%m-%d")
        return None

    def _build_query(
        self,
        language: str = "",
        period: str = "weekly",
        search: str = "",
    ) -> str:
        """Construct the GitHub search query string."""
        query_parts = []

        if search:
            query_parts.append(search.strip())
        if language:
            query_parts.append(f"language:{language}")

        since = self._get_period_date(period)
        if since:
            query_parts.append(f"created:>={since}")

        if not query_parts:
            query_parts.append("created:>2020-01-01")

        return " ".join(query_parts)

    def fetch_trending(
        self,
        language: str = "",
        period: str = "weekly",
        search: str = "",
        sort: str = "stars",
        per_page: Optional[int] = None,
        use_cache: bool = True,
    ) -> list[dict]:
        """
        Fetch trending repositories from GitHub.

        Args:
            language: Filter by programming language (empty = all).
            period: One of 'weekly', 'monthly', 'yearly', 'all'.
            search: Free-text search query.
            sort: Sort field ('stars', 'forks', 'updated').
            per_page: Number of results to return.
            use_cache: Whether to use Django cache.

        Returns:
            A list of repository dicts from the GitHub API.

        Raises:
            GitHubServiceError: If the API request fails.
        """
        if per_page is None:
            per_page = self.per_page

        cache_key = self._build_cache_key(language, period, search, sort)

        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug("Cache hit for %s", cache_key)
                return cached

        query = self._build_query(language=language, period=period, search=search)

        params = {
            "q": query,
            "sort": sort,
            "order": "desc",
            "per_page": per_page,
        }

        url = f"{self.base_url}/search/repositories"

        try:
            response = requests.get(
                url,
                params=params,
                headers=self._headers(),
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.exceptions.Timeout as exc:
            logger.error("GitHub API timeout: %s", exc)
            raise GitHubServiceError("The GitHub API request timed out. Please try again.")
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response else 0
            if status == 403:
                logger.error("GitHub API rate limit exceeded: %s", exc)
                raise GitHubServiceError(
                    "GitHub API rate limit exceeded. Please add a GITHUB_TOKEN or try again later."
                )
            if status == 422:
                logger.error("GitHub API validation error: %s", exc)
                raise GitHubServiceError("Invalid search query. Please adjust your filters.")
            logger.error("GitHub API HTTP error: %s", exc)
            raise GitHubServiceError(f"GitHub API error (HTTP {status}). Please try again.")
        except requests.exceptions.RequestException as exc:
            logger.error("GitHub API request failed: %s", exc)
            raise GitHubServiceError("Unable to connect to GitHub. Please check your connection.")

        data = response.json()
        items = data.get("items", [])

        if use_cache:
            cache.set(cache_key, items, timeout=getattr(settings, "CACHES", {}).get("default", {}).get("TIMEOUT", 600))

        return items

    def get_rate_limit(self) -> dict:
        """Get the current GitHub API rate limit status."""
        url = f"{self.base_url}/rate_limit"
        try:
            response = requests.get(url, headers=self._headers(), timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            logger.error("Failed to fetch rate limit: %s", exc)
            return {}
