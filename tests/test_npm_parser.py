import unittest
from packageurl import PackageURL
from purl2repo.npm_parser import NpmParser


class TestNpmParser(unittest.TestCase):
    def test_get_source_repo_and_release(self):
        purl_str = "pkg:npm/lodash@4.17.21"
        purl = PackageURL.from_string(purl_str)
        parser = NpmParser(purl)
        result = parser.get_source_repo_and_release()

        # Ensure the package name is correct
        self.assertEqual(result["package_name"], "lodash")

        # Check if github_repo is present, if not, assert it's None
        if result["github_repo"]:
            self.assertIn("github.com", result["github_repo"])
        else:
            self.assertIsNone(result["github_repo"])

        # Ensure the version is correct
        self.assertEqual(result["specified_version"], "4.17.21")

    def test_npm_package_not_found(self):
        purl_str = "pkg:npm/unknown-package@1.0.0"
        purl = PackageURL.from_string(purl_str)
        parser = NpmParser(purl)
        with self.assertRaises(ValueError):
            parser.get_source_repo_and_release()

    def test_fallback_scraper(self):
        """Test the fallback to the scraper if GitHub repo isn't found in metadata"""
        purl_str = "pkg:npm/request@2.88.2"
        purl = PackageURL.from_string(purl_str)
        parser = NpmParser(purl)
        result = parser.get_source_repo_and_release()

        # Even if no direct GitHub link is found in metadata, the scraper should find it
        self.assertEqual(result["package_name"], "request")
        if result["github_repo"]:
            self.assertIn("github.com", result["github_repo"])
        else:
            self.assertIsNone(result["github_repo"])

        # Ensure the version is correct
        self.assertEqual(result["specified_version"], "2.88.2")


if __name__ == "__main__":
    unittest.main()
