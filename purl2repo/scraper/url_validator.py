import requests

class URLValidator:
    @staticmethod
    def validate_vcs_url(repo_url, version):
        """Validates if the repository release or tag URL is valid."""
        release_url = f"{repo_url}/releases/tag/{version}"
        tag_url = f"{repo_url}/tags/{version}"
        commits_url = f"{repo_url}/commits/tag/{version}"

        if URLValidator.url_has_valid_content(release_url):
            return release_url
        if URLValidator.url_has_valid_content(tag_url):
            return tag_url
        if URLValidator.url_has_valid_content(commits_url):
            return commits_url

        return None

    @staticmethod
    def url_has_valid_content(url):
        """Checks if the URL has valid content (non-empty page, valid tag)."""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                if "No commits history" in response.text or "There aren’t any releases" in response.text:
                    return False
                return True
        except requests.RequestException as e:
            print(f"Error validating URL {url}: {e}")
        return False
