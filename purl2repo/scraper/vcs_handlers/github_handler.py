from ..url_validator import URLValidator
import logging

logger = logging.getLogger(__name__)

class GitHubHandler:
    @staticmethod
    def get_release_url(repo_url, version):
        """Fetches and validates the release or tag URL from GitHub."""
        # Ensure no trailing slash in the base repo URL
        repo_url = repo_url.rstrip("/")

        # Format URLs for different paths
        release_url = f"{repo_url}/releases/tag/{version}"
        tag_url = f"{repo_url}/tags/{version}"
        commit_tag_url = f"{repo_url}/commits/tag/{version}"

        # Validate release URL
        logger.debug(f"Validating release URL: {release_url}")
        is_valid, error = URLValidator.validate_release_url(release_url)
        if is_valid:
            logger.debug(f"Valid release found: {release_url}")
            return release_url
        else:
            logger.debug(f"Release URL validation failed: {error}")

        # Validate tag URL
        logger.debug(f"Validating tag URL: {tag_url}")
        is_valid, error = URLValidator.validate_release_url(tag_url)
        if is_valid:
            logger.debug(f"Valid tag found: {tag_url}")
            return tag_url
        else:
            logger.debug(f"Tag URL validation failed: {error}")

        # Validate commit tag URL as a last resort
        logger.debug(f"Validating commit tag URL: {commit_tag_url}")
        is_valid, error = URLValidator.validate_commit_url(commit_tag_url)
        if is_valid:
            if "No Commit History" in error:
                logger.debug(f"Commit tag URL is valid but has no commit history: {commit_tag_url}")
                return None  # Ensuring that we don't return an empty commit history URL
            else:
                logger.debug(f"Valid commit tag used as fallback: {commit_tag_url}")
                return commit_tag_url
        else:
            logger.debug(f"Commit tag URL validation failed: {error}")

        # If all fail, log that no release was found and return None
        logger.debug(f"No valid release or tag found for {repo_url} and version {version}")
        return None
