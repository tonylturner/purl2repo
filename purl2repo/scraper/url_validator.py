import requests
import logging

logger = logging.getLogger(__name__)

class URLValidator:
    @staticmethod
    def validate_release_url(url):
        """Validates if a given URL for a release or tag is valid."""
        # Convert SCM URLs to standard HTTP URLs
        url = URLValidator.convert_scm_url(url)

        try:
            logger.debug(f"Validating release URL: {url}")
            response = requests.get(url, timeout=10)

            # Log response status and content length
            logger.debug(f"Response status for {url}: {response.status_code}, Content length: {len(response.text)}")

            # Log part of the response content to ensure it's being captured
            logger.debug(f"Response content preview for {url}: {response.text[:500]}")  # First 500 chars

            # Check if the URL gives a 404 error
            if response.status_code == 404:
                logger.debug(f"URL not found (404): {url}")
                return False, "404 Not Found"

            # Check for empty releases
            if "There aren’t any releases here" in response.text:
                logger.debug(f"No releases found for URL: {url}")
                return False, "No Releases"

            # Check for empty commit history
            if "No commits history" in response.text or "There are no commits" in response.text:
                logger.debug(f"No commit history found for URL: {url}")
                return False, "No Commit History"

            # If it's a valid tag page, return success
            if response.status_code == 200 and ('releases/tag' in url or 'tags/' in url):
                logger.debug(f"Valid release or tag URL: {url}")
                return True, None

            logger.debug(f"Valid but unhandled URL: {url}")
            return True, None
        except requests.RequestException as e:
            logger.error(f"Error validating URL: {url} - {str(e)}")
            return False, f"Error: {str(e)}"

    @staticmethod
    def validate_commit_url(url):
        """Validates if a given URL for a commit tag is valid."""
        # Convert SCM URLs to standard HTTP URLs
        url = URLValidator.convert_scm_url(url)

        try:
            logger.debug(f"Validating commit URL: {url}")
            response = requests.get(url, timeout=10)

            # Log response status and content length
            logger.debug(f"Response status for {url}: {response.status_code}, Content length: {len(response.text)}")

            # Log part of the response content to ensure it's being captured
            logger.debug(f"Response content preview for {url}: {response.text[:500]}")  # First 500 chars

            # Check if the URL gives a 404 error
            if response.status_code == 404:
                logger.debug(f"Commit URL not found (404): {url}")
                return False, "404 Not Found"

            # Check for empty commit history
            if "No commits history" in response.text or "There are no commits" in response.text:
                logger.debug(f"No commit history found for URL: {url}")
                return False, "No Commit History"

            logger.debug(f"Valid commit URL with history: {url}")
            return True, None
        except requests.RequestException as e:
            logger.error(f"Error validating commit URL: {url} - {str(e)}")
            return False, f"Error: {str(e)}"

    @staticmethod
    def convert_scm_url(url):
        """Converts SCM formatted URLs to HTTP if possible."""
        if url.startswith("scm:git:git@github.com"):
            # Convert from git@github.com:owner/repo.git to https://github.com/owner/repo
            return url.replace("scm:git:git@", "https://").replace(":", "/").replace(".git", "")
        elif url.startswith("scm:git:git://github.com") or url.startswith("git://github.com"):
            # Convert from git://github.com/owner/repo.git to https://github.com/owner/repo
            return url.replace("scm:git:git://", "https://").replace("git://", "https://").replace(".git", "")
        elif url.startswith("scm:git:https://github.com"):
            # Remove the 'scm:git:' prefix from https URLs
            return url.replace("scm:git:", "")
        elif url.startswith("scm:hg:http://bitbucket.org"):
            # Convert Mercurial Bitbucket URL from http to https
            return url.replace("scm:hg:http://", "https://")
        elif url.startswith("scm:hg:https://bitbucket.org"):
            # Remove the 'scm:hg:' part for Bitbucket
            return url.replace("scm:hg:", "")
        # Return the original URL if no conversion is needed
        return url
