"""Official purl-spec examples for purl types supported by purl2repo.

Fixtures are vendored from:
https://github.com/package-url/purl-spec/tree/main/tests/types
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from purl2repo.models import ParsedPurl
from purl2repo.purl.normalize import normalize_purl
from purl2repo.purl.parse import parse_purl, purl_to_string

SUPPORTED_TYPE_FIXTURES = (
    "bitbucket-test.json",
    "cargo-test.json",
    "generic-test.json",
    "github-test.json",
    "golang-test.json",
    "huggingface-test.json",
    "maven-test.json",
    "mlflow-test.json",
    "npm-test.json",
    "nuget-test.json",
    "pypi-test.json",
)

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "purl_spec"


def _load_examples(test_type: str) -> list[pytest.ParamSpecArg]:
    examples: list[pytest.ParamSpecArg] = []
    for fixture_name in SUPPORTED_TYPE_FIXTURES:
        payload = json.loads((FIXTURE_DIR / fixture_name).read_text(encoding="utf-8"))
        for index, example in enumerate(payload["tests"]):
            if example["test_type"] != test_type or example.get("expected_failure"):
                continue
            examples.append(
                pytest.param(
                    example,
                    id=f"{fixture_name.removesuffix('-test.json')}:{test_type}:{index}",
                )
            )
    return examples


def _parsed_to_spec_dict(parsed: ParsedPurl) -> dict[str, Any]:
    return {
        "type": parsed.type,
        "namespace": parsed.namespace,
        "name": parsed.name,
        "version": parsed.version,
        "qualifiers": parsed.qualifiers or None,
        "subpath": parsed.subpath,
    }


@pytest.mark.parametrize("example", _load_examples("parse"))
def test_parse_supported_purl_spec_examples(example: dict[str, Any]) -> None:
    parsed = parse_purl(example["input"])

    assert _parsed_to_spec_dict(parsed) == example["expected_output"]


@pytest.mark.parametrize("example", _load_examples("roundtrip"))
def test_roundtrip_supported_purl_spec_examples(example: dict[str, Any]) -> None:
    assert normalize_purl(example["input"]) == example["expected_output"]


@pytest.mark.parametrize("example", _load_examples("build"))
def test_build_supported_purl_spec_examples(example: dict[str, Any]) -> None:
    data = example["input"]
    parsed = ParsedPurl(
        raw=example["expected_output"],
        type=data["type"],
        namespace=data["namespace"],
        name=data["name"],
        version=data["version"],
        qualifiers=data["qualifiers"] or {},
        subpath=data["subpath"],
    )

    assert purl_to_string(parsed) == example["expected_output"]
