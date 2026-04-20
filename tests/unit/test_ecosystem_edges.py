import xml.etree.ElementTree as ET

import pytest
from tests.conftest import FakeHttpClient, load_text

from purl2repo.ecosystems.base import EcosystemResolver
from purl2repo.ecosystems.cargo import CargoResolver
from purl2repo.ecosystems.maven import MavenResolver
from purl2repo.ecosystems.npm import NpmResolver, npm_package_name
from purl2repo.ecosystems.pypi import PyPiResolver
from purl2repo.models import ParsedPurl, RepositoryCandidate
from purl2repo.purl.parse import parse_purl


def test_pypi_ignores_malformed_metadata_and_accepts_repo_like_project_url():
    parsed = parse_purl("pkg:pypi/example")
    candidates = PyPiResolver().extract_candidates(
        parsed,
        {
            "info": {
                "project_urls": {
                    "Docs": "https://example.readthedocs.io",
                    "Tracker": "https://github.com/org/repo/issues",
                    1: "https://github.com/ignored/repo",
                },
                "home_page": None,
            }
        },
    )

    assert candidates[0].normalized_url == "https://github.com/org/repo"


def test_pypi_ignores_funding_project_urls_when_source_exists():
    parsed = parse_purl("pkg:pypi/example")
    candidates = PyPiResolver().extract_candidates(
        parsed,
        {
            "info": {
                "project_urls": {
                    "Funding": "https://github.com/sponsors/example",
                    "Source": "https://codeberg.org/example/project",
                }
            }
        },
    )

    assert [candidate.normalized_url for candidate in candidates] == [
        "https://codeberg.org/example/project"
    ]


def test_pypi_handles_missing_info():
    assert PyPiResolver().extract_candidates(parse_purl("pkg:pypi/example"), {"info": []}) == []
    assert PyPiResolver().fallback_scrape_pages(parse_purl("pkg:pypi/example"), {"info": []}) == [
        "https://pypi.org/project/example/"
    ]


def test_npm_package_name_and_repository_string():
    parsed = parse_purl("pkg:npm/%40scope/name")
    assert npm_package_name(parsed) == "@scope/name"

    candidates = NpmResolver().extract_candidates(
        parsed,
        {
            "repository": "git@github.com:scope/name.git",
            "homepage": "https://scope.github.io/name",
        },
    )
    assert candidates[0].normalized_url == "https://github.com/scope/name"
    assert NpmResolver().fallback_scrape_pages(
        parsed,
        {
            "homepage": "https://example.com/project",
            "repository": {"url": "https://github.com/scope/name"},
        },
    ) == [
        "https://www.npmjs.com/package/@scope/name",
        "https://example.com/project",
        "https://github.com/scope/name",
    ]


def test_npm_ignores_missing_version_metadata():
    parsed = parse_purl("pkg:npm/react@19.0.0")
    assert NpmResolver().extract_candidates(parsed, {"versions": []}) == []


def test_cargo_handles_missing_crate_and_versionless_fetch():
    resolver = CargoResolver()
    assert resolver.extract_candidates(parse_purl("pkg:cargo/example"), {"crate": []}) == []

    client = FakeHttpClient({"https://crates.io/api/v1/crates/example": {"crate": {}}})
    assert resolver.fetch_metadata(parse_purl("pkg:cargo/example"), client) == {"crate": {}}
    assert resolver.fallback_scrape_pages(
        parse_purl("pkg:cargo/example"),
        {"crate": {"homepage": "https://example.com/project"}},
    ) == ["https://crates.io/crates/example", "https://example.com/project"]


def test_maven_versionless_fetches_latest_pom():
    parsed = parse_purl("pkg:maven/org.example/demo")
    client = FakeHttpClient(
        text_payloads={
            "https://repo1.maven.org/maven2/org/example/demo/maven-metadata.xml": (
                "<metadata><versioning><latest>1.2.3</latest></versioning></metadata>"
            ),
            "https://repo1.maven.org/maven2/org/example/demo/1.2.3/demo-1.2.3.pom": load_text(
                "maven/log4j-core.pom"
            ),
        }
    )

    metadata = MavenResolver().fetch_metadata(parsed, client)

    assert metadata["effective_version"] == "1.2.3"
    assert metadata["pom"]["scm"]["url"] == "https://github.com/apache/logging-log4j2"


def test_maven_fetches_parent_pom_when_child_has_no_scm():
    parsed = parse_purl("pkg:maven/org.example/child@1.0.0")
    child = """
    <project xmlns="http://maven.apache.org/POM/4.0.0">
      <parent>
        <groupId>org.example</groupId>
        <artifactId>parent</artifactId>
        <version>1.0.0</version>
      </parent>
    </project>
    """
    parent = """
    <project xmlns="http://maven.apache.org/POM/4.0.0">
      <scm><url>https://github.com/example/parent</url></scm>
    </project>
    """
    client = FakeHttpClient(
        text_payloads={
            "https://repo1.maven.org/maven2/org/example/child/1.0.0/child-1.0.0.pom": child,
            "https://repo1.maven.org/maven2/org/example/parent/1.0.0/parent-1.0.0.pom": parent,
        }
    )

    metadata = MavenResolver().fetch_metadata(parsed, client)
    candidates = MavenResolver().extract_candidates(parsed, metadata)

    assert candidates[0].normalized_url == "https://github.com/example/parent"
    assert candidates[0].source == "pom_parent_scm"


def test_maven_empty_namespace_and_missing_xml_children():
    assert MavenResolver().fetch_metadata(parse_purl("pkg:maven/demo"), FakeHttpClient()) == {}
    candidates = MavenResolver().extract_candidates(
        parse_purl("pkg:maven/org.example/demo"),
        {"pom": {"scm": {"connection": ""}, "url": "https://example.com/project"}},
    )
    assert candidates
    assert MavenResolver().fallback_scrape_pages(
        parse_purl("pkg:maven/org.example/demo"),
        {"pom": {"url": "https://example.com/project"}},
    ) == [
        "https://central.sonatype.com/artifact/org.example/demo",
        "https://example.com/project",
    ]


def test_maven_branch_edges():
    resolver = MavenResolver()
    parsed = parse_purl("pkg:maven/org.example/demo")

    assert resolver._latest_version(parse_purl("pkg:maven/demo"), FakeHttpClient()) == ""
    assert resolver._fetch_parent_pom({"artifactId": "x", "version": "1"}, FakeHttpClient()) is None
    assert resolver._fetch_parent_pom({"groupId": "g", "version": "1"}, FakeHttpClient()) is None
    assert resolver._fetch_parent_pom({"groupId": "g", "artifactId": "a"}, FakeHttpClient()) is None
    assert resolver._fetch_parent_chain({"groupId": "g"}, FakeHttpClient()) == []

    candidates = resolver.extract_candidates(
        parsed,
        {
            "pom": [],
            "parent_poms": [
                [],
                {"scm": []},
                {"scm": {"url": "https://github.com/example/parent"}},
            ],
        },
    )
    assert candidates[0].normalized_url == "https://github.com/example/parent"
    assert candidates[0].source == "pom_parent_scm"

    dict_parent_candidates = resolver.extract_candidates(
        parsed,
        {"pom": {}, "parent_poms": {"scm": {"url": "https://github.com/example/dict-parent"}}},
    )
    assert dict_parent_candidates[0].normalized_url == "https://github.com/example/dict-parent"
    assert dict_parent_candidates[0].source == "pom_parent_scm"


def test_maven_invalid_xml_raises():
    with pytest.raises(ET.ParseError):
        MavenResolver().fetch_metadata(
            parse_purl("pkg:maven/org.example/demo@1.0.0"),
            FakeHttpClient(
                text_payloads={
                    "https://repo1.maven.org/maven2/org/example/demo/1.0.0/demo-1.0.0.pom": "<"
                }
            ),
        )


class DummyResolver(EcosystemResolver):
    ecosystem = "dummy"
    metadata_source = "dummy"

    def fetch_metadata(self, parsed: ParsedPurl, client: FakeHttpClient) -> dict:
        _ = parsed, client
        return {}

    def extract_candidates(self, parsed: ParsedPurl, metadata: dict) -> list[RepositoryCandidate]:
        _ = parsed, metadata
        return []


def test_base_adapter_defaults():
    adapter = DummyResolver()
    parsed = parse_purl("pkg:pypi/demo")

    assert adapter.fallback_scrape_pages(parsed, {}) == []
    assert adapter.resolve_release_link(parsed, None, {}, None) is None
