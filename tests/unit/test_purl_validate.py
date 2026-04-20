import pytest

from purl2repo.errors import InvalidPurlError
from purl2repo.purl.validate import validate_purl


@pytest.mark.parametrize(
    "purl",
    [
        "pkg:pypi/requests?arch",
        "pkg:pypi/requests?arch=",
        "pkg:pypi/requests?=x",
        "pkg:pypi/re%ZZquests",
        "pkg:pypi/requests@1@2",
    ],
)
def test_validation_rejects_malformed_purls(purl):
    with pytest.raises(InvalidPurlError):
        validate_purl(purl)


def test_validation_returns_parsed_model():
    parsed = validate_purl("pkg:github/package-url/purl-spec#docs")
    assert parsed.type == "github"
    assert parsed.namespace == "package-url"
    assert parsed.name == "purl-spec"
    assert parsed.subpath == "docs"


def test_validation_accepts_authority_style_separator_from_purl_spec_examples():
    parsed = validate_purl("pkg://pypi/requests")

    assert parsed.type == "pypi"
    assert parsed.name == "requests"
