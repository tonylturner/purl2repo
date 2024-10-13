import requests
import logging
from .scraper.url_validator import URLValidator  # Assuming this is where the URLValidator is located
from .scraper.vcs_handlers.github_handler import GitHubHandler


logger = logging.getLogger(__name__)

class BaseParser:
    def __init__(self, purl):
        self.purl = purl
        self.package_name = purl.name
        self.specified_version = purl.version

        if not self.specified_version:
            raise ValueError("A specific version must be provided in the purl.")

    def get_metadata(self):
        """To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement this method")

    def extract_vcs_repo(self, metadata):
        """To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement this method")

    def get_source_repo_and_release(self):
        metadata = self.get_metadata()
        vcs_repo = self.extract_vcs_repo(metadata)

        # If a GitHub repository is found, check for the release or tag URL
        if vcs_repo:
            release_url = self.get_vcs_release_url(vcs_repo, self.specified_version)
        else:
            release_url = None

        return {
            "package_name": self.package_name,
            "vcs_repo": vcs_repo,
            "specified_version": self.specified_version,
            "release_url": release_url,
        }

    def fallback_scraper(self, metadata, package_manager):
        """Fallback method to use the scraper if no GitHub repository is found."""
        from .scraper import Scraper  # Import scraper only when needed to avoid circular imports

        return Scraper.find_vcs_repo(metadata, package_manager)

    def get_github_release_url(self, repo_url, version):
        """Uses the scraper to get the release URL."""
        from .scraper import Scraper

        return Scraper.get_github_release_url(repo_url, version)

    def get_vcs_release_url(self, repo_url, version):
        """Fetches the release or tag URL from a VCS repository for a given version."""
        logger.debug(f"Fetching release or tag URL for repo {repo_url} and version {version}")

        # Use URLValidator to validate potential release or tag URLs
        handler = GitHubHandler()
        release_url = handler.get_release_url(repo_url, version)
        
        if release_url:
            logger.debug(f"Valid release or tag URL found: {release_url}")
            return release_url
        else:
            logger.debug(f"No valid release or tag URL found for repo {repo_url} and version {version}")
            return None
