from tests.conftest import FakeHttpClient

from purl2repo.purl.parse import parse_purl
from purl2repo.resolution.deps_dev import fetch_deps_dev_candidates


def test_deps_dev_extracts_version_candidates():
    client = FakeHttpClient(
        json_payloads={
            "https://api.deps.dev/v3/systems/NPM/packages/%40scope%2Fdemo/versions/1.2.3": {
                "links": [
                    {"label": "SOURCE_REPO", "url": "https://github.com/org/demo"},
                    {"label": "ISSUE_TRACKER", "url": "https://github.com/org/demo/issues"},
                    {"label": "HOMEPAGE", "url": "https://docs.example.com/demo"},
                ],
                "relatedProjects": [
                    {
                        "projectKey": {"id": "gitlab.com/group/demo"},
                        "relationType": "SOURCE_REPO",
                    },
                    {
                        "projectKey": {"id": "github.com/org/demo/issues"},
                        "relationType": "ISSUE_TRACKER",
                    },
                ],
                "slsaProvenances": [{"sourceRepository": "https://github.com/org/demo-provenance"}],
                "attestations": [{"sourceRepository": "https://github.com/org/demo-attestation"}],
            }
        }
    )

    candidates, evidence, warnings = fetch_deps_dev_candidates(
        parse_purl("pkg:npm/%40scope/demo@1.2.3"),
        client,
    )

    assert [candidate.source for candidate in candidates] == [
        "deps_dev_related_project",
        "deps_dev_link",
        "deps_dev_attestation",
        "deps_dev_attestation",
    ]
    assert [candidate.normalized_url for candidate in candidates] == [
        "https://gitlab.com/group/demo",
        "https://github.com/org/demo",
        "https://github.com/org/demo-provenance",
        "https://github.com/org/demo-attestation",
    ]
    assert evidence == ["Queried deps.dev as a third-party fallback metadata source"]
    assert warnings == []


def test_deps_dev_uses_default_version_for_versionless_purls():
    client = FakeHttpClient(
        json_payloads={
            "https://api.deps.dev/v3/systems/PYPI/packages/demo": {
                "versions": [
                    {"versionKey": {"version": "0.9.0"}},
                    {"isDefault": True, "versionKey": {"version": "1.0.0"}},
                ]
            },
            "https://api.deps.dev/v3/systems/PYPI/packages/demo/versions/1.0.0": {
                "links": [{"label": "SOURCE_REPO", "url": "https://github.com/org/demo"}]
            },
        }
    )

    candidates, evidence, warnings = fetch_deps_dev_candidates(
        parse_purl("pkg:pypi/demo"),
        client,
    )

    assert candidates[0].normalized_url == "https://github.com/org/demo"
    assert "Used deps.dev default version 1.0.0 for repository fallback" in evidence
    assert warnings == []


def test_deps_dev_returns_empty_for_unsupported_types_and_lookup_failures():
    unsupported = fetch_deps_dev_candidates(
        parse_purl("pkg:huggingface/org/model"),
        FakeHttpClient(),
    )
    missing = fetch_deps_dev_candidates(
        parse_purl("pkg:pypi/demo"),
        FakeHttpClient(),
    )

    assert unsupported == ([], [], [])
    assert missing[0] == []
    assert any("deps.dev package lookup failed" in warning for warning in missing[2])
