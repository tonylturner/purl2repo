import unittest
from packageurl import PackageURL
from purl2repo.cargo_parser import CargoParser

class TestCargoParser(unittest.TestCase):
    def test_get_source_repo_and_release(self):
        purl_str = "pkg:cargo/rand@0.8.3"
        purl = PackageURL.from_string(purl_str)
        parser = CargoParser(purl)
        result = parser.get_source_repo_and_release()
        
        # Ensure the package name is correct
        self.assertEqual(result['package_name'], 'rand')
        
        # Check if github_repo is present, if not, assert it's None
        if result['github_repo']:
            self.assertIn('github.com', result['github_repo'])
        else:
            self.assertIsNone(result['github_repo'])
        
        # Ensure the version is correct
        self.assertEqual(result['specified_version'], '0.8.3')

    def test_cargo_package_not_found(self):
        purl_str = "pkg:cargo/unknown-crate@1.0.0"
        purl = PackageURL.from_string(purl_str)
        parser = CargoParser(purl)
        with self.assertRaises(ValueError):
            parser.get_source_repo_and_release()

if __name__ == '__main__':
    unittest.main()

