import requests
from .base_parser import BaseParser

class NpmParser(BaseParser):
    def get_metadata(self):
        url = f"https://registry.npmjs.org/{self.package_name}/{self.specified_version}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(f"Version {self.specified_version} of package {self.package_name} not found on npm.")

    def extract_github_repo(self, metadata):
        repo_info = metadata.get('repository', {})
        if 'url' in repo_info and "github.com" in repo_info['url']:
            return repo_info['url'].replace('git+', '').replace('.git', '')
        return None  # Return None if no GitHub repo found
