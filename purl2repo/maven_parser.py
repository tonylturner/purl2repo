import requests
import logging
import xml.etree.ElementTree as ET
from .base_parser import BaseParser
from .scraper import Scraper  # Importing the scraper for fallback logic

logger = logging.getLogger(__name__)

class MavenParser(BaseParser):
    def get_metadata(self):
        """Fetches the Maven package metadata by retrieving the POM file."""
        group_id_path = self.purl.namespace.replace('.', '/')
        url = f"https://repo1.maven.org/maven2/{group_id_path}/{self.package_name}/{self.specified_version}/{self.package_name}-{self.specified_version}.pom"
        logger.debug(f"Fetching Maven POM file from {url}")

        response = requests.get(url)
        if response.status_code == 200:
            logger.debug(f"POM file fetched successfully for {self.package_name} version {self.specified_version}")
            return self.parse_maven_pom(response.content)
        else:
            logger.error(f"Version {self.specified_version} of package {self.package_name} not found on Maven.")
            raise ValueError(f"Version {self.specified_version} of package {self.package_name} not found on Maven.")

    def extract_vcs_repo(self, metadata):
        """Extracts the VCS (GitHub, GitLab, Bitbucket) repository link from the Maven metadata."""
        scm_url = metadata.get("scm_url")
        if scm_url:
            # Clean up the URL and ensure it starts with a valid scheme
            cleaned_url = self.clean_scm_url(scm_url)
            if cleaned_url and any(vcs in cleaned_url.lower() for vcs in ["github.com", "gitlab.com", "bitbucket.org"]):
                return cleaned_url
            else:
                logger.debug(f"No valid SCM URL found for {self.package_name}.")
        
        # If no valid SCM URL found in metadata, fallback to scraper
        logger.debug(f"Falling back to scraper for {self.package_name}.")
        homepage_url = metadata.get("homepage_url")
        vcs_url = self.fallback_to_scraper(homepage_url)
        if vcs_url:
            return vcs_url
        
        logger.debug(f"No SCM URL or VCS found for {self.package_name}.")
        return None

    def fallback_to_scraper(self, homepage_url):
        """Uses the scraper to attempt finding a VCS repository if not present in the metadata."""
        if homepage_url:
            logger.debug(f"Scraping homepage {homepage_url} for VCS information.")
            try:
                return Scraper.find_vcs_repo(homepage_url, "maven")
            except Exception as e:
                logger.error(f"Error using scraper to find VCS repo: {e}")
        return None

    def clean_scm_url(self, scm_url):
        """Cleans SCM URLs and ensures they are in the correct format."""
        # Remove "scm:git:" if present and ensure it starts with https://
        if scm_url.startswith("scm:git:"):
            scm_url = scm_url.replace("scm:git:", "")

        # If it's git@github.com style, convert to https://github.com/ style
        if scm_url.startswith("git@"):
            scm_url = scm_url.replace("git@", "https://").replace(":", "/")

        # Ensure the URL starts with "https://"
        if not scm_url.startswith("https://"):
            if scm_url.startswith("http://"):
                scm_url = scm_url.replace("http://", "https://")
            elif scm_url.startswith("https///"):
                scm_url = scm_url.replace("https///", "https://")

        # Remove any redundant slashes (e.g., 'https///' or 'https://https///')
        scm_url = scm_url.replace("///", "/").strip()

        return scm_url

    def parse_maven_pom(self, pom_content):
        """Parses the Maven POM file to extract SCM information."""
        try:
            root = ET.fromstring(pom_content)
            scm = root.find("{http://maven.apache.org/POM/4.0.0}scm")
            if scm is not None:
                connection = scm.find("{http://maven.apache.org/POM/4.0.0}connection")
                url = scm.find("{http://maven.apache.org/POM/4.0.0}url")
                return {
                    "scm_url": connection.text if connection is not None else (url.text if url is not None else None)
                }
            else:
                logger.debug("No SCM section found in the POM file.")
                return {}
        except ET.ParseError as e:
            logger.error(f"Error parsing Maven POM file: {e}")
            raise ValueError(f"Error parsing Maven POM file for {self.package_name}.")

    def check_for_latest_version(self):
        """Handles @latest logic by checking for the latest version in Maven metadata."""
        group_id_path = self.purl.namespace.replace('.', '/')
        url = f"https://repo1.maven.org/maven2/{group_id_path}/{self.package_name}/maven-metadata.xml"
        logger.debug(f"Fetching Maven metadata for latest version: {url}")

        try:
            response = requests.get(url)
            if response.status_code == 200:
                metadata = self.parse_maven_metadata(response.content)
                latest_version = metadata.get("latest_version")
                if latest_version:
                    logger.debug(f"Latest version found: {latest_version}")
                    self.specified_version = latest_version
                    return self.get_metadata()
                else:
                    raise ValueError(f"No latest version found for {self.package_name}.")
            else:
                raise ValueError(f"Failed to retrieve metadata for {self.package_name}.")
        except requests.RequestException as e:
            logger.error(f"Error fetching latest version metadata: {e}")
            raise ValueError(f"Error fetching latest version metadata for {self.package_name} from Maven.")

    def parse_maven_metadata(self, xml_content):
        """Parses the Maven metadata XML to extract relevant version information."""
        try:
            root = ET.fromstring(xml_content)
            versioning = root.find("versioning")
            latest_version = versioning.find("latest").text if versioning.find("latest") else None
            release_version = versioning.find("release").text if versioning.find("release") else None
            return {
                "latest_version": latest_version,
                "release_version": release_version,
                "versions": [v.text for v in versioning.findall("versions/version")]
            }
        except ET.ParseError as e:
            logger.error(f"Error parsing Maven metadata XML: {e}")
            raise ValueError(f"Error parsing Maven metadata XML for {self.package_name}.")
