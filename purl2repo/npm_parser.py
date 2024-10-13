import requests
from .base_parser import BaseParser

class NpmParser(BaseParser):
    def get_metadata(self):
        """Fetches the package metadata from the NPM registry."""
        url = f"https://registry.npmjs.org/{self.package_name}/{self.specified_version}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(f"Version {self.specified_version} of package {self.package_name} not found on npm.")

    def extract_github_repo(self, metadata):
        """Extracts the GitHub repository link from the NPM metadata."""
        # First, check the 'repository' field for GitHub URLs
        repo_info = metadata.get('repository', {})
        if 'url' in repo_info and "github.com" in repo_info['url']:
            # Clean up the URL (remove git+ and .git if present)
            return repo_info['url'].replace('git+', '').replace('.git', '')

        # Fallback: If no GitHub repository is found, use the fallback_scraper from BaseParser
        return self.fallback_scraper(metadata, 'npm')
