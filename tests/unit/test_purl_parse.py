from purl2repo.errors import InvalidPurlError
from purl2repo.purl.normalize import normalize_purl
from purl2repo.purl.parse import parse_purl


def test_parse_valid_versioned_pypi_purl():
    parsed = parse_purl("pkg:pypi/requests@2.31.0")

    assert parsed.type == "pypi"
    assert parsed.namespace is None
    assert parsed.name == "requests"
    assert parsed.version == "2.31.0"
    assert parsed.qualifiers == {}
    assert parsed.subpath is None


def test_parse_valid_versionless_purls():
    assert parse_purl("pkg:pypi/requests").version is None
    npm = parse_purl("pkg:npm/%40types/node")
    assert npm.namespace == "@types"
    assert npm.name == "node"
    maven = parse_purl("pkg:maven/org.apache.logging.log4j/log4j-core")
    assert maven.namespace == "org.apache.logging.log4j"
    assert maven.name == "log4j-core"


def test_parse_qualifiers_and_subpath():
    parsed = parse_purl("pkg:deb/debian/curl@7.50.3-1?distro=jessie&arch=i386#src/main")

    assert parsed.namespace == "debian"
    assert parsed.qualifiers == {"arch": "i386", "distro": "jessie"}
    assert parsed.subpath == "src/main"
    assert (
        normalize_purl(parsed.raw)
        == "pkg:deb/debian/curl@7.50.3-1?arch=i386&distro=jessie#src/main"
    )


def test_invalid_missing_type_and_name():
    for purl in ("pkg:/requests", "pkg:pypi/", "pypi/requests", "pkg:pypi"):
        try:
            parse_purl(purl)
        except InvalidPurlError:
            pass
        else:
            raise AssertionError(f"Expected invalid PURL: {purl}")
