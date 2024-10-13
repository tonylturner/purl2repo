import requests

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
        # Format the release and tag URLs for GitHub, GitLab, and Bitbucket
        release_urls = [
            f"{repo_url}/releases/tag/{version}",  # GitHub
            f"{repo_url}/-/tags/{version}",  # GitLab
            f"{repo_url}/commits/tag/{version}"  # Bitbucket
        ]

        for url in release_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return url
            except requests.RequestException as e:
                print(f"Error checking release URL {url}: {e}")

        return None
