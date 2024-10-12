import requests
from .base_parser import BaseParser

class CargoParser(BaseParser):
    def get_metadata(self):
        url = f"https://crates.io/api/v1/crates/{self.package_name}/{self.specified_version}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(f"Version {self.specified_version} of crate {self.package_name} not found on crates.io.")

    def extract_github_repo(self, metadata):
        repo = metadata.get('crate', {}).get('repository', None)
        if repo:
            return repo
        return None
