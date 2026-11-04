from django.contrib import admin

from .models import Repository


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = [
        "full_name",
        "language",
        "stargazers_count",
        "forks_count",
        "open_issues_count",
        "fetched_at",
    ]
    list_filter = ["language", "is_fork", "is_archived", "fetched_at"]
    search_fields = ["full_name", "owner", "description"]
    readonly_fields = ["fetched_at", "github_id"]
    date_hierarchy = "fetched_at"
    ordering = ["-stargazers_count"]

    fieldsets = (
        (
            "Basic Info",
            {
                "fields": (
                    "github_id",
                    "full_name",
                    "owner",
                    "html_url",
                    "description",
                    "language",
                )
            },
        ),
        (
            "Stats",
            {
                "fields": (
                    "stargazers_count",
                    "forks_count",
                    "open_issues_count",
                    "watchers_count",
                    "size",
                )
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "default_branch",
                    "created_at",
                    "updated_at",
                    "pushed_at",
                    "is_fork",
                    "is_archived",
                    "license_name",
                    "topics",
                    "fetched_at",
                )
            },
        ),
    )
