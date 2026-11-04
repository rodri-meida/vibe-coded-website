from django.db import models
from django.utils import timezone


class Repository(models.Model):
    """A cached snapshot of a GitHub repository."""

    github_id = models.PositiveBigIntegerField(unique=True, db_index=True)
    full_name = models.CharField(max_length=255, db_index=True)
    owner = models.CharField(max_length=255)
    html_url = models.URLField()
    description = models.TextField(blank=True)
    language = models.CharField(max_length=100, blank=True, db_index=True)
    stargazers_count = models.PositiveIntegerField(default=0, db_index=True)
    forks_count = models.PositiveIntegerField(default=0)
    open_issues_count = models.PositiveIntegerField(default=0)
    watchers_count = models.PositiveIntegerField(default=0)
    size = models.PositiveIntegerField(default=0)
    default_branch = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    pushed_at = models.DateTimeField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now=True)
    is_fork = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    license_name = models.CharField(max_length=100, blank=True)
    topics = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-stargazers_count", "-forks_count"]
        verbose_name = "Repository"
        verbose_name_plural = "Repositories"
        indexes = [
            models.Index(fields=["language", "-stargazers_count"]),
            models.Index(fields=["-updated_at"]),
        ]

    def __str__(self):
        return self.full_name

    @property
    def owner_name(self):
        return self.owner

    @property
    def repo_name(self):
        return self.full_name.split("/")[-1] if "/" in self.full_name else self.full_name

    @classmethod
    def from_github_item(cls, item: dict) -> "Repository":
        """Create or update a Repository instance from a GitHub API item."""
        license_info = item.get("license") or {}
        return cls(
            github_id=item["id"],
            full_name=item["full_name"],
            owner=item["owner"]["login"],
            html_url=item["html_url"],
            description=item.get("description") or "",
            language=item.get("language") or "",
            stargazers_count=item.get("stargazers_count", 0),
            forks_count=item.get("forks_count", 0),
            open_issues_count=item.get("open_issues_count", 0),
            watchers_count=item.get("watchers_count", 0),
            size=item.get("size", 0),
            default_branch=item.get("default_branch", ""),
            created_at=item.get("created_at"),
            updated_at=item.get("updated_at"),
            pushed_at=item.get("pushed_at"),
            is_fork=item.get("fork", False),
            is_archived=item.get("archived", False),
            license_name=license_info.get("name", ""),
            topics=item.get("topics", []),
        )
