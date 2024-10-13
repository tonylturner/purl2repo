import requests
from .base_parser import BaseParser
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class PyPiParser(BaseParser):
    def __init__(self, purl):
        super().__init__(purl)

        # Check if the version is set to 'latest' and replace it with the latest version from PyPI
        if self.specified_version == 'latest':
            self.specified_version = self.fetch_latest_version()
            logger.debug(f"Replaced 'latest' with actual version: {self.specified_version}")

    def fetch_latest_version(self):
        """Fetches the latest version of the package from PyPI."""
        url = f"https://pypi.org/pypi/{self.package_name}/json"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                latest_version = data['info']['version']
                logger.debug(f"Latest version for {self.package_name} is {latest_version}")
                return latest_version
            else:
                logger.error(f"Failed to fetch latest version for {self.package_name}. Status code: {response.status_code}")
                raise ValueError(f"Package {self.package_name} not found on PyPI.")
        except requests.RequestException as e:
            logger.error(f"Error fetching latest version for {self.package_name}: {e}")
            raise ValueError(f"Error fetching latest version for {self.package_name} from PyPI")

    def get_metadata(self):
        """Fetches the package metadata from the PyPI API."""
        url = f"https://pypi.org/pypi/{self.package_name}/{self.specified_version}/json"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(
                f"Version {self.specified_version} of package {self.package_name} not found on PyPI."
            )

    def extract_vcs_repo(self, metadata):
        """Extracts the VCS (GitHub, GitLab, Bitbucket) repository link from the PyPI metadata."""
        # First check the 'project_urls' field for any VCS repo
        project_urls = metadata.get("info", {}).get("project_urls", {})
        for label, url in project_urls.items():
            if any(
                vcs in url.lower()
                for vcs in ["github.com", "gitlab.com", "bitbucket.org"]
            ):
                return url

        # Check the 'home_page' field
        home_page = metadata.get("info", {}).get("home_page", "")
        if home_page and any(
            vcs in home_page.lower()
            for vcs in ["github.com", "gitlab.com", "bitbucket.org"]
        ):
            return home_page
        elif home_page:
            # Scrape the homepage for a potential VCS link
            vcs_repo = self.scrape_homepage_for_vcs(home_page)
            if vcs_repo:
                return vcs_repo

        # Check the 'download_url' field
        download_url = metadata.get("info", {}).get("download_url", "")
        if any(
            vcs in download_url.lower()
            for vcs in ["github.com", "gitlab.com", "bitbucket.org"]
        ):
            return download_url

        # Check the package description for VCS links (less reliable)
        description = metadata.get("info", {}).get("description", "")
        if any(
            vcs in description.lower()
            for vcs in ["github.com", "gitlab.com", "bitbucket.org"]
        ):
            return self.extract_first_vcs_link_from_text(description)

        # Final fallback: Use the scraper to find a VCS repo if none found in metadata
        return self.fallback_scraper(metadata.get("info", {}), "pypi")

    def scrape_homepage_for_vcs(self, homepage_url):
        """Scrapes a homepage URL to find a VCS (GitHub, GitLab, Bitbucket) link."""
        try:
            response = requests.get(homepage_url, timeout=10)
            if response.status_code != 200:
                return None
            soup = BeautifulSoup(response.text, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"].lower()
                if any(
                    vcs in href for vcs in ["github.com", "gitlab.com", "bitbucket.org"]
                ):
                    return a_tag["href"]
        except requests.RequestException as e:
            logger.error(f"Error scraping homepage {homepage_url}: {e}")
        return None

    def extract_first_vcs_link_from_text(self, text):
        """Helper function to extract the first VCS (GitHub, GitLab, Bitbucket) link from a block of text."""
        import re

        pattern = r"https?://(?:github|gitlab|bitbucket)\.com/[^\s]+"
        match = re.search(pattern, text)
        if match:
            return match.group(0)
        return None
