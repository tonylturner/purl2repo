import requests
from .base_parser import BaseParser

class CargoParser(BaseParser):
    def get_metadata(self):
        """Fetches metadata from the Crates.io API for the specified package and version."""
        url = f"https://crates.io/api/v1/crates/{self.package_name}/{self.specified_version}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(f"Version {self.specified_version} of crate {self.package_name} not found on crates.io.")

    def extract_github_repo(self, metadata):
        """Extracts the GitHub repository link from the Crates.io metadata."""
        # First, check the 'repository' field in the Crates.io metadata
        repo = metadata.get('crate', {}).get('repository', None)
        if repo and "github.com" in repo:
            return repo

        # Fallback: If no GitHub repository is found, use the fallback_scraper from BaseParser
        return self.fallback_scraper(metadata.get('crate', {}), 'cargo')
