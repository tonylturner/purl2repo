from .vcs_handlers.github_handler import GitHubHandler
from .vcs_handlers.gitlab_handler import GitLabHandler
from .vcs_handlers.bitbucket_handler import BitbucketHandler
from .url_validator import URLValidator


class Scraper:
    @staticmethod
    def scrape_vcs_repo(url):
        """Scrapes the provided URL for GitHub, GitLab, or Bitbucket links."""
        if "github.com" in url:
            return GitHubHandler.extract_vcs_links(url)
        elif "gitlab.com" in url:
            return GitLabHandler.extract_vcs_links(url)
        elif "bitbucket.org" in url:
            return BitbucketHandler.extract_vcs_links(url)
        return []

    @staticmethod
    def validate_release_url(repo_url, version):
        """Validates the release URL for a repository."""
        return URLValidator.validate_vcs_url(repo_url, version)
