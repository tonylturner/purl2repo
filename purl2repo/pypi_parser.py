import requests
from .base_parser import BaseParser

class PyPiParser(BaseParser):
    def get_metadata(self):
        url = f"https://pypi.org/pypi/{self.package_name}/{self.specified_version}/json"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(f"Version {self.specified_version} of package {self.package_name} not found on PyPI.")

    def extract_github_repo(self, metadata):
        project_urls = metadata.get('info', {}).get('project_urls', {})
        for label, url in project_urls.items():
            if "github.com" in url.lower():
                return url
        return None  # Return None if no GitHub repo found

