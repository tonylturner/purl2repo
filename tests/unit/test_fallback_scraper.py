import pytest
from tests.conftest import FakeHttpClient

from purl2repo.errors import MetadataFetchError
from purl2repo.models import ResolverSettings
from purl2repo.purl.parse import parse_purl
from purl2repo.resolution.engine import ResolutionEngine
from purl2repo.resolution.scraper import (
    FallbackScraper,
    default_fallback_pages,
    scraped_to_repository_candidate,
    should_scrape_purl,
)


def test_scraper_extracts_structured_candidates_and_enforces_page_cap():
    client = FakeHttpClient(
        text_payloads={
            "https://example.com/pkg": '<a href="https://github.com/org/repo">Source</a>',
            "https://example.com/second": '<a href="https://gitlab.com/group/project">Code</a>',
        }
    )

    scraped = FallbackScraper(client, max_pages=2).scrape(
        parse_purl("pkg:pypi/demo"),
        [
            "https://example.com/pkg",
            "https://example.com/pkg",
            "ftp://example.com/nope",
            "https://example.com/second",
            "https://example.com/third",
        ],
    )

    assert [candidate.normalized_url for candidate in scraped] == [
        "https://github.com/org/repo",
        "https://gitlab.com/group/project",
    ]
    assert scraped[0].source_page == "https://example.com/pkg"
    assert scraped[0].extraction_method == "html_anchor"
    assert scraped[0].label_context == "Source"
    assert scraped[0].to_dict()["score_cap"] == 60.0


def test_scraped_candidate_conversion():
    client = FakeHttpClient(
        text_payloads={"https://example.com/pkg": '<a href="/org/repo.git">Repo</a>'}
    )
    scraped = FallbackScraper(client).scrape(
        parse_purl("pkg:pypi/demo"),
        ["https://example.com/pkg"],
    )[0]

    candidate = scraped_to_repository_candidate(scraped)

    assert candidate is not None
    assert candidate.source == "scrape"
    assert candidate.normalized_url == "https://example.com/org/repo"
    assert "Score cap: 60" in candidate.reasons


def test_default_fallback_pages():
    assert default_fallback_pages(parse_purl("pkg:pypi/demo"), {}) == [
        "https://pypi.org/project/demo/"
    ]
    assert default_fallback_pages(parse_purl("pkg:npm/%40scope/demo"), {}) == [
        "https://www.npmjs.com/package/@scope/demo"
    ]
    assert default_fallback_pages(parse_purl("pkg:cargo/demo"), {}) == [
        "https://crates.io/crates/demo"
    ]
    assert default_fallback_pages(parse_purl("pkg:maven/org.example/demo"), {}) == [
        "https://central.sonatype.com/artifact/org.example/demo"
    ]
    assert default_fallback_pages(parse_purl("pkg:maven/demo"), {}) == []


def test_scraper_exclusions():
    assert not should_scrape_purl(parse_purl("pkg:github/org/repo"))
    assert not should_scrape_purl(parse_purl("pkg:bitbucket/org/repo"))
    assert not should_scrape_purl(parse_purl("pkg:huggingface/org/model"))
    assert should_scrape_purl(parse_purl("pkg:pypi/demo"))


def test_engine_does_not_scrape_when_structured_metadata_is_usable(monkeypatch):
    engine = ResolutionEngine(ResolverSettings())
    engine.client = FakeHttpClient(
        {
            "https://pypi.org/pypi/demo/json": {
                "info": {"project_urls": {"Source": "https://github.com/org/demo"}}
            }
        }
    )

    def fail_scrape(parsed, pages):
        _ = parsed, pages
        raise AssertionError("scraper should not run")

    monkeypatch.setattr(engine.scraper, "scrape", fail_scrape)

    result = engine.resolve("pkg:pypi/demo")

    assert result.repository_url == "https://github.com/org/demo"
    assert all(candidate.source != "scrape" for candidate in result.repository_candidates)


def test_engine_uses_scraper_when_structured_metadata_has_no_repo():
    engine = ResolutionEngine(ResolverSettings())
    engine.client = FakeHttpClient(
        json_payloads={"https://pypi.org/pypi/demo/json": {"info": {}}},
        text_payloads={
            "https://pypi.org/project/demo/": '<a href="https://github.com/org/demo">Source</a>'
        },
    )
    engine.scraper = FallbackScraper(engine.client)

    result = engine.resolve("pkg:pypi/demo")

    assert result.repository_url == "https://github.com/org/demo"
    assert result.confidence == "low"
    assert result.repository_candidates[0].source == "scrape"
    assert (
        "Used fallback scraping because structured metadata did not yield "
        "a usable repository candidate" in result.warnings
    )


def test_docs_homepage_does_not_block_fallback_scraping():
    engine = ResolutionEngine(ResolverSettings())
    engine.client = FakeHttpClient(
        json_payloads={
            "https://pypi.org/pypi/demo/json": {
                "info": {"home_page": "https://docs.example.com/demo"}
            }
        },
        text_payloads={
            "https://pypi.org/project/demo/": "",
            "https://docs.example.com/demo": (
                '<a href="https://github.com/org/demo">Source repository</a>'
            ),
        },
    )
    engine.scraper = FallbackScraper(engine.client)

    result = engine.resolve("pkg:pypi/demo")

    assert result.repository_url == "https://github.com/org/demo"
    assert result.repository_candidates[0].source == "scrape"
    assert all(
        candidate.normalized_url != "https://docs.example.com/demo"
        for candidate in result.repository_candidates
    )


def test_engine_non_strict_scraper_metadata_failure_returns_warning(monkeypatch):
    engine = ResolutionEngine(ResolverSettings())
    engine.client = FakeHttpClient({"https://pypi.org/pypi/demo/json": {"info": {}}})
    engine.scraper = FallbackScraper(engine.client)

    def fail_scrape(parsed, pages):
        _ = parsed, pages
        raise MetadataFetchError("down")

    monkeypatch.setattr(engine.scraper, "scrape", fail_scrape)

    result = engine.resolve("pkg:pypi/demo")

    assert result.repository_url is None
    assert "Fallback scraping failed" in result.warnings


def test_engine_scraper_failure_propagates_in_strict_mode():
    engine = ResolutionEngine(ResolverSettings(strict=True))
    engine.client = FakeHttpClient({"https://pypi.org/pypi/demo/json": {"info": {}}})
    engine.scraper = FallbackScraper(engine.client)

    with pytest.raises(AssertionError, match="Unexpected text URL"):
        engine.resolve("pkg:pypi/demo")
