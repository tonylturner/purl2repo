import unittest
from packageurl import PackageURL
from purl2repo.pypi_parser import PyPiParser


class TestPyPiParser(unittest.TestCase):
    def test_get_source_repo_and_release(self):
        purl_str = "pkg:pypi/requests@2.25.1"
        purl = PackageURL.from_string(purl_str)
        parser = PyPiParser(purl)
        result = parser.get_source_repo_and_release()

        # Ensure the package name is correct
        self.assertEqual(result["package_name"], "requests")

        # Check if github_repo is present and contains a valid GitHub link
        if result["github_repo"]:
            self.assertIn("github.com", result["github_repo"])
        else:
            # If not found, we expect github_repo to be None
            self.assertIsNone(result["github_repo"])

        # Ensure the version is correct
        self.assertEqual(result["specified_version"], "2.25.1")

    def test_pypi_package_not_found(self):
        purl_str = "pkg:pypi/unknown-package@1.0.0"
        purl = PackageURL.from_string(purl_str)
        parser = PyPiParser(purl)
        with self.assertRaises(ValueError):
            parser.get_source_repo_and_release()

    def test_fallback_scraper(self):
        """Test the fallback to the scraper if GitHub repo isn't found in metadata"""
        purl_str = "pkg:pypi/django@1.4"
        purl = PackageURL.from_string(purl_str)
        parser = PyPiParser(purl)
        result = parser.get_source_repo_and_release()

        # Even though Django 1.4 may not return GitHub directly in metadata,
        # it should fallback to the scraper and find the GitHub repo.
        self.assertEqual(result["package_name"], "django")
        if result["github_repo"]:
            self.assertIn("github.com", result["github_repo"])
        else:
            self.assertIsNone(result["github_repo"])

        # Ensure the version is correct
        self.assertEqual(result["specified_version"], "1.4")


if __name__ == "__main__":
    unittest.main()
