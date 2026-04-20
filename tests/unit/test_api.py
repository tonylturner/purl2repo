import pytest
from tests.conftest import load_json, load_text

from purl2repo import Resolver, parse_purl, resolve, resolve_release, resolve_repository
from purl2repo.errors import NoReleaseFoundError, UnsupportedEcosystemError
from purl2repo.resolution.engine import ResolutionEngine


def test_top_level_parse_api():
    parsed = parse_purl("pkg:npm/%40types/node@20.0.0")
    assert parsed.namespace == "@types"
    assert parsed.name == "node"


def test_resolve_pypi_with_fixture(fake_http_factory):
    fake_http_factory(
        {
            "https://pypi.org/pypi/requests/2.31.0/json": load_json("pypi/requests.json"),
        }
    )

    result = resolve("pkg:pypi/requests@2.31.0")

    assert result.repository_url == "https://github.com/psf/requests"
    assert result.repository_type == "github"
    assert result.release_link is not None
    assert result.release_link.url.endswith("/releases/tag/v2.31.0")
    assert result.confidence == "high"
    assert result.metadata_sources == ["pypi-json"]


def test_verify_release_links_selects_existing_candidate(fake_http_factory):
    fake_http_factory(
        {
            "https://pypi.org/pypi/requests/2.31.0/json": load_json("pypi/requests.json"),
        }
    )

    with Resolver(verify_release_links=True) as resolver:
        result = resolver.resolve("pkg:pypi/requests@2.31.0")

    assert result.release_link is not None
    assert result.release_link.url.endswith("/v2.31.0")
    assert "Verified version-specific release link exists" in result.evidence


def test_verify_release_links_warns_when_unverified(fake_http_factory):
    fake = fake_http_factory(
        {
            "https://pypi.org/pypi/requests/2.31.0/json": load_json("pypi/requests.json"),
        }
    )
    fake.url_exists = lambda url, ttl_seconds=900: (
        "/releases/" not in url and "/tags/" not in url and "/tree/" not in url
    )

    with Resolver(verify_release_links=True) as resolver:
        result = resolver.resolve("pkg:pypi/requests@2.31.0")

    assert result.release_link is None
    assert "Inferred release link could not be verified" in result.warnings


def test_top_level_repo_and_release_apis(fake_http_factory):
    fake_http_factory(
        {
            "https://pypi.org/pypi/requests/2.31.0/json": load_json("pypi/requests.json"),
        }
    )

    repo = resolve_repository("pkg:pypi/requests@2.31.0")
    release = resolve_release("pkg:pypi/requests@2.31.0")

    assert repo.release_link is None
    assert release.release_link is not None


def test_resolve_versionless_skips_release(fake_http_factory):
    fake_http_factory({"https://pypi.org/pypi/requests/json": load_json("pypi/requests.json")})

    with Resolver() as resolver:
        result = resolver.resolve("pkg:pypi/requests")

    assert result.repository_url == "https://github.com/psf/requests"
    assert result.release_link is None
    assert "Version not supplied; skipped version-specific release resolution" in result.warnings


def test_resolve_npm_cargo_and_maven_with_fixtures(fake_http_factory):
    fake_http_factory(
        {
            "https://registry.npmjs.org/react": load_json("npm/react.json"),
            "https://crates.io/api/v1/crates/rand": load_json("cargo/rand.json"),
        },
        {
            (
                "https://repo1.maven.org/maven2/org/apache/logging/log4j/"
                "log4j-core/2.22.1/log4j-core-2.22.1.pom"
            ): load_text("maven/log4j-core.pom"),
        },
    )

    with Resolver() as resolver:
        npm = resolver.resolve("pkg:npm/react@18.2.0")
        cargo = resolver.resolve("pkg:cargo/rand@0.8.5")
        maven = resolver.resolve("pkg:maven/org.apache.logging.log4j/log4j-core@2.22.1")

    assert npm.repository_url == "https://github.com/facebook/react"
    assert cargo.repository_url == "https://github.com/rust-random/rand"
    assert maven.repository_url == "https://github.com/apache/logging-log4j2"


def test_resolve_many_reuses_resolver(fake_http_factory):
    fake_http_factory({"https://pypi.org/pypi/requests/json": load_json("pypi/requests.json")})

    with Resolver() as resolver:
        results = list(resolver.resolve_many(["pkg:pypi/requests"]))

    assert len(results) == 1
    assert results[0].repository_url == "https://github.com/psf/requests"


def test_no_network_returns_warning_without_strict():
    with Resolver(no_network=True) as resolver:
        result = resolver.resolve("pkg:pypi/requests")

    assert result.repository_url is None
    assert result.confidence == "none"
    assert result.warnings == ["Could not fetch metadata from pypi-json"]


def test_strict_unsupported_and_release_failures(fake_http_factory):
    with pytest.raises(UnsupportedEcosystemError):
        ResolutionEngine(parse_settings()).resolve("pkg:gem/rails@1.0.0")

    fake_http_factory(
        {
            "https://pypi.org/pypi/requests/2.31.0/json": {
                "info": {"project_urls": {"Source": "https://git.example.com/org/repo.git"}}
            }
        }
    )
    with Resolver(strict=True) as resolver, pytest.raises(NoReleaseFoundError):
        resolver.resolve_release("pkg:pypi/requests@2.31.0")


def parse_settings():
    from purl2repo.models import ResolverSettings

    return ResolverSettings()
