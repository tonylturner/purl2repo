from .vcs_handlers.github_handler import GitHubHandler
from .vcs_handlers.gitlab_handler import GitLabHandler
from .vcs_handlers.bitbucket_handler import BitbucketHandler
from .url_validator import URLValidator
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

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

    @staticmethod
    def find_vcs_repo(homepage_url, package_manager):
        """
        Attempts to scrape the homepage of a project to locate a VCS repository (GitHub, GitLab, Bitbucket).
        This is a fallback mechanism when the VCS repo is not provided in the metadata.
        """
        try:
            response = requests.get(homepage_url, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to fetch homepage: {homepage_url}")
                return None
            
            soup = BeautifulSoup(response.text, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"].lower()
                if "github.com" in href or "gitlab.com" in href or "bitbucket.org" in href:
                    logger.debug(f"VCS repo link found on homepage {homepage_url}: {a_tag['href']}")
                    return a_tag["href"]

            logger.debug(f"No VCS repo found on homepage {homepage_url} for {package_manager}.")
        except requests.RequestException as e:
            logger.error(f"Error scraping homepage {homepage_url}: {e}")
        
        return None
