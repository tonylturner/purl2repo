"""Compare official supported purl-spec examples against live resolution.

This script is intentionally non-gating: unresolved or unverified examples are
reported for investigation, but they do not cause a non-zero exit code. The
fixtures are parser conformance examples first, not guaranteed live packages.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from purl2repo import Resolver
from purl2repo.models import ParsedPurl, ResolutionResult
from purl2repo.purl.normalize import normalize_purl
from purl2repo.purl.parse import purl_to_string

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

SCRAPE_SKIPPED_TYPES = {"bitbucket", "generic", "github", "huggingface", "mlflow"}


@dataclass(frozen=True)
class ReportRow:
    purl_type: str
    purl: str
    repository_url: str | None
    repository_kind: str | None
    repository_validated: bool
    release_url: str | None
    release_kind: str | None
    confidence: str
    scraping_used: bool
    warnings: list[str]
    assessment: str


def main() -> int:
    args = _parse_args()
    rows = build_report(
        fixture_dir=args.fixture_dir,
        timeout=args.timeout,
        verify_release_links=args.verify_release_links,
    )
    if args.json:
        print(json.dumps([asdict(row) for row in rows], indent=2 if args.pretty else None))
    else:
        print_markdown_report(rows, include_resolved=args.include_resolved)
    return 0


def build_report(
    *,
    fixture_dir: Path,
    timeout: float,
    verify_release_links: bool,
) -> list[ReportRow]:
    rows: list[ReportRow] = []
    examples = _load_unique_examples(fixture_dir)
    with Resolver(
        timeout=timeout,
        use_cache=True,
        strict=False,
        verify_release_links=verify_release_links,
    ) as resolver:
        for purl_type, purls in sorted(examples.items()):
            for purl in sorted(purls):
                try:
                    result = resolver.resolve(purl)
                except Exception as exc:  # pragma: no cover - defensive report behavior
                    rows.append(_error_row(purl_type, purl, exc))
                else:
                    rows.append(_row_from_result(purl_type, purl, result))
    return rows


def _load_unique_examples(fixture_dir: Path) -> dict[str, set[str]]:
    examples: dict[str, set[str]] = defaultdict(set)
    for fixture_name in SUPPORTED_TYPE_FIXTURES:
        purl_type = fixture_name.removesuffix("-test.json")
        payload = json.loads((fixture_dir / fixture_name).read_text(encoding="utf-8"))
        for example in payload["tests"]:
            if example.get("expected_failure"):
                continue
            test_type = example["test_type"]
            if test_type in {"parse", "roundtrip"}:
                examples[purl_type].add(normalize_purl(example["input"]))
            elif test_type == "build":
                examples[purl_type].add(_build_purl(example["input"], example["expected_output"]))
    return examples


def _build_purl(data: dict[str, Any], expected_output: str) -> str:
    parsed = ParsedPurl(
        raw=expected_output,
        type=data["type"],
        namespace=data["namespace"],
        name=data["name"],
        version=data["version"],
        qualifiers=data["qualifiers"] or {},
        subpath=data["subpath"],
    )
    return purl_to_string(parsed)


def _row_from_result(purl_type: str, purl: str, result: ResolutionResult) -> ReportRow:
    repository_validated = bool(
        result.repository_url
        and any(
            evidence == f"Validated repository URL: {result.repository_url}"
            for evidence in result.evidence
        )
    )
    scraping_used = any(
        "fallback scraping" in item.lower() for item in [*result.evidence, *result.warnings]
    )
    return ReportRow(
        purl_type=purl_type,
        purl=purl,
        repository_url=result.repository_url,
        repository_kind=result.repository_kind,
        repository_validated=repository_validated,
        release_url=result.release_link.url if result.release_link else None,
        release_kind=result.release_link.kind if result.release_link else None,
        confidence=result.confidence,
        scraping_used=scraping_used,
        warnings=result.warnings,
        assessment=_assess_result(purl_type, purl, result, repository_validated, scraping_used),
    )


def _error_row(purl_type: str, purl: str, exc: Exception) -> ReportRow:
    return ReportRow(
        purl_type=purl_type,
        purl=purl,
        repository_url=None,
        repository_kind=None,
        repository_validated=False,
        release_url=None,
        release_kind=None,
        confidence="error",
        scraping_used=False,
        warnings=[f"{type(exc).__name__}: {exc}"],
        assessment="resolver raised unexpectedly; investigate this example",
    )


def _assess_result(
    purl_type: str,
    purl: str,
    result: ResolutionResult,
    repository_validated: bool,
    scraping_used: bool,
) -> str:
    if repository_validated:
        if result.release_link and result.release_link.kind == "commit":
            return "validated repository; commit-style version resolved to commit link"
        if scraping_used:
            return "validated repository recovered by fallback scraping"
        return "validated repository from structured/direct resolution"
    if result.repository_url:
        return "repository returned but validation could not confirm it"
    if purl_type == "generic" and "requires one of" in " ".join(result.warnings):
        return "no improvement expected; generic example lacks explicit URL qualifiers"
    if purl_type in {"mlflow", "bitbucket"}:
        return "upstream example appears private, stale, or environment-specific"
    if purl_type in SCRAPE_SKIPPED_TYPES:
        return "scraping intentionally skipped for this purl type"
    if scraping_used:
        return "scraper ran but did not find a verifiable repository"
    if any("fetch metadata" in warning for warning in result.warnings):
        return "metadata lookup failed; fallback pages may be stale or absent"
    return "unresolved; candidate for future resolver or scraper improvements"


def print_markdown_report(rows: list[ReportRow], *, include_resolved: bool) -> None:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        if row.repository_validated:
            status = "validated"
        elif row.repository_url:
            status = "unverified"
        else:
            status = "none"
        counts[row.purl_type][status] += 1
        counts[row.purl_type]["total"] += 1

    print("# purl-spec Resolution Report")
    print()
    print("This report is informational. Unresolved examples do not fail builds.")
    print()
    print("| Type | Total | Validated | Unverified | No repo |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for purl_type in sorted(counts):
        stats = counts[purl_type]
        print(
            f"| `{purl_type}` | {stats['total']} | {stats['validated']} | "
            f"{stats['unverified']} | {stats['none']} |"
        )

    interesting = [
        row for row in rows if include_resolved or not row.repository_validated or row.scraping_used
    ]
    if not interesting:
        return

    print()
    print("## Examples To Review")
    print()
    for row in interesting:
        print(f"- `{row.purl_type}` `{row.purl}`")
        print(f"  - repo: `{row.repository_url or 'not found'}`")
        print(f"  - confidence: `{row.confidence}`")
        print(f"  - scraping used: `{str(row.scraping_used).lower()}`")
        print(f"  - assessment: {row.assessment}")
        if row.release_url:
            print(f"  - version reference: `{row.release_kind}` `{row.release_url}`")
        for warning in row.warnings[:4]:
            print(f"  - warning: {warning}")
        if len(row.warnings) > 4:
            print(f"  - warning: ... {len(row.warnings) - 4} more")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        default=Path("tests/fixtures/purl_spec"),
        help="Directory containing vendored purl-spec type fixtures.",
    )
    parser.add_argument("--timeout", type=float, default=5.0, help="HTTP timeout in seconds.")
    parser.add_argument(
        "--verify-release-links",
        action="store_true",
        help="Verify tag, source, package, revision, and commit links.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument(
        "--include-resolved",
        action="store_true",
        help="Include fully validated examples in the review section.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
