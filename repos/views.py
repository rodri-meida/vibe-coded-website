from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.conf import settings

from .services import GitHubService, GitHubServiceError

# Available filter options for the UI
LANGUAGES = [
    ("", "All Languages"),
    ("JavaScript", "JavaScript"),
    ("TypeScript", "TypeScript"),
    ("Python", "Python"),
    ("Go", "Go"),
    ("Rust", "Rust"),
    ("Java", "Java"),
    ("C++", "C++"),
    ("C#", "C#"),
    ("PHP", "PHP"),
    ("Ruby", "Ruby"),
    ("Swift", "Swift"),
    ("Kotlin", "Kotlin"),
    ("Dart", "Dart"),
    ("Scala", "Scala"),
    ("Shell", "Shell"),
]

PERIODS = [
    ("weekly", "This Week"),
    ("monthly", "This Month"),
    ("yearly", "This Year"),
    ("all", "All Time"),
]

SORTS = [
    ("stars", "Stars"),
    ("forks", "Forks"),
    ("updated", "Recently Updated"),
]


def _get_valid_value(value: str, valid_values: set, default: str) -> str:
    """Validate a query parameter against allowed values."""
    return value if value in valid_values else default


def home(request):
    """Home page showing trending GitHub repositories."""
    service = GitHubService()

    # Get and validate query parameters
    language = request.GET.get("language", "")
    period = _get_valid_value(request.GET.get("period", "weekly"), {p[0] for p in PERIODS}, "weekly")
    search = request.GET.get("search", "").strip()
    sort = _get_valid_value(request.GET.get("sort", "stars"), {s[0] for s in SORTS}, "stars")

    # Pagination
    page_number = request.GET.get("page", 1)

    repositories = []
    error = None
    total_count = 0
    rate_limit = None

    try:
        raw_items = service.fetch_trending(
            language=language,
            period=period,
            search=search,
            sort=sort,
        )

        total_count = len(raw_items)

        # Normalize GitHub API items into a consistent shape for the template
        for item in raw_items:
            repositories.append(
                {
                    "github_id": item["id"],
                    "full_name": item["full_name"],
                    "owner": item["owner"]["login"],
                    "html_url": item["html_url"],
                    "description": item.get("description") or "",
                    "language": item.get("language") or "",
                    "stargazers_count": item.get("stargazers_count", 0),
                    "forks_count": item.get("forks_count", 0),
                    "open_issues_count": item.get("open_issues_count", 0),
                    "watchers_count": item.get("watchers_count", 0),
                    "size": item.get("size", 0),
                    "default_branch": item.get("default_branch", ""),
                    "created_at": item.get("created_at", ""),
                    "updated_at": item.get("updated_at", ""),
                    "pushed_at": item.get("pushed_at", ""),
                    "is_fork": item.get("fork", False),
                    "is_archived": item.get("archived", False),
                    "license_name": (item.get("license") or {}).get("name", ""),
                    "topics": item.get("topics", []),
                }
            )

        # Apply sorting in Python (GitHub API sorts by stars by default;
        # we re-sort here so the UI sort buttons work without extra API calls)
        if sort == "forks":
            repositories.sort(key=lambda r: r["forks_count"], reverse=True)
        elif sort == "updated":
            repositories.sort(key=lambda r: r["updated_at"], reverse=True)
        else:
            repositories.sort(key=lambda r: r["stargazers_count"], reverse=True)

        # Paginate results
        paginator = Paginator(repositories, settings.REPOS_PER_PAGE)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        repositories = page_obj.object_list

        # Fetch rate limit info for display
        rate_limit = service.get_rate_limit()

    except GitHubServiceError as exc:
        error = str(exc)
    except Exception as exc:  # noqa: BLE001
        error = f"Unexpected error: {exc}"

    context = {
        "repositories": repositories,
        "page_obj": page_obj if repositories or error is None else None,
        "is_paginated": page_obj.has_other_pages() if "page_obj" in locals() else False,
        "languages": LANGUAGES,
        "periods": PERIODS,
        "sorts": SORTS,
        "selected_language": language,
        "selected_period": period,
        "selected_sort": sort,
        "search_query": search,
        "error": error,
        "result_count": total_count,
        "rate_limit": rate_limit,
    }
    return render(request, "repos/home.html", context)
