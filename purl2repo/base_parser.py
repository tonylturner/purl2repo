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

    def extract_github_repo(self, metadata):
        """To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement this method")

    def get_source_repo_and_release(self):
        metadata = self.get_metadata()
        github_repo = self.extract_github_repo(metadata)
        return {
            "package_name": self.package_name,
            "github_repo": github_repo,
            "specified_version": self.specified_version,
        }
