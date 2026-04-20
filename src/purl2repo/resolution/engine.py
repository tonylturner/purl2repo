"""Resolution pipeline orchestration."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from purl2repo.ecosystems.base import EcosystemResolver, Metadata
from purl2repo.ecosystems.cargo import CargoResolver
from purl2repo.ecosystems.maven import MavenResolver
from purl2repo.ecosystems.npm import NpmResolver
from purl2repo.ecosystems.pypi import PyPiResolver
from purl2repo.errors import (
    MetadataFetchError,
    NoReleaseFoundError,
    NoRepositoryFoundError,
    UnsupportedEcosystemError,
)
from purl2repo.hosts.base import HostAdapter
from purl2repo.hosts.bitbucket import BitbucketAdapter
from purl2repo.hosts.generic_git import GenericGitAdapter
from purl2repo.hosts.github import GitHubAdapter
from purl2repo.hosts.gitlab import GitLabAdapter
from purl2repo.http.client import HttpClient
from purl2repo.models import (
    ParsedPurl,
    ReleaseLink,
    RepositoryCandidate,
    ResolutionResult,
    ResolverSettings,
)
from purl2repo.purl.parse import parse_purl
from purl2repo.resolution import evidence as evidence_messages
from purl2repo.resolution.cache import ResponseCache
from purl2repo.resolution.scorer import confidence_from_score, score_candidates
from purl2repo.resolution.scraper import (
    FallbackScraper,
    default_fallback_pages,
    scraped_to_repository_candidate,
    should_scrape_purl,
)

ECOSYSTEMS: dict[str, type[EcosystemResolver]] = {
    "pypi": PyPiResolver,
    "npm": NpmResolver,
    "cargo": CargoResolver,
    "maven": MavenResolver,
}

HOSTS: dict[str, HostAdapter] = {
    "github.com": GitHubAdapter(),
    "gitlab.com": GitLabAdapter(),
    "bitbucket.org": BitbucketAdapter(),
}
GENERIC_HOST = GenericGitAdapter()


class ResolutionEngine:
    def __init__(self, settings: ResolverSettings) -> None:
        self.settings = settings
        self.cache = ResponseCache(settings.cache_dir) if settings.use_cache else None
        self.client = HttpClient(settings, self.cache)
        self.scraper = FallbackScraper(self.client)

    def close(self) -> None:
        self.client.close()

    def parse(self, purl: str) -> ParsedPurl:
        return parse_purl(purl)

    def resolve(self, purl: str, *, include_release: bool = True) -> ResolutionResult:
        parsed = self.parse(purl)
        adapter = self._adapter_for(parsed)
        warnings: list[str] = []
        evidence: list[str] = []
        metadata_sources = [adapter.metadata_source]
        metadata: Metadata = {}

        try:
            metadata = adapter.fetch_metadata(parsed, self.client)
            evidence.append(evidence_messages.fetched(adapter.metadata_source))
        except MetadataFetchError:
            if self.settings.strict:
                raise
            warnings.append(f"Could not fetch metadata from {adapter.metadata_source}")
            return self._empty_result(parsed, warnings, evidence, metadata_sources)

        candidates = score_candidates(adapter.extract_candidates(parsed, metadata), parsed)
        structured_confidence = confidence_from_score(candidates[0].score if candidates else 0.0)
        if structured_confidence == "none" and should_scrape_purl(parsed):
            scrape_pages = [
                *adapter.fallback_scrape_pages(parsed, metadata),
                *default_fallback_pages(parsed, metadata),
            ]
            try:
                scraped = self.scraper.scrape(parsed, scrape_pages)
            except MetadataFetchError:
                if self.settings.strict:
                    raise
                scraped = []
                warnings.append("Fallback scraping failed")
            scraped_candidates = [
                scraped_to_repository_candidate(candidate) for candidate in scraped
            ]
            scrape_repository_candidates = [
                candidate for candidate in scraped_candidates if candidate is not None
            ]
            if scrape_repository_candidates:
                warnings.append(evidence_messages.used_fallback_scraping())
                evidence.append(evidence_messages.used_fallback_scraping())
                candidates = score_candidates(
                    [*candidates, *scrape_repository_candidates],
                    parsed,
                )
        best = candidates[0] if candidates else None
        confidence = confidence_from_score(best.score if best else 0.0)

        if best is None:
            warnings.append(evidence_messages.no_repository_warning())
            if self.settings.strict:
                raise NoRepositoryFoundError(f"No repository found for {parsed.raw}")
        elif confidence == "none":
            warnings.append(evidence_messages.weak_candidate_warning())
            if self.settings.strict:
                raise NoRepositoryFoundError(
                    f"Only weak repository candidates found for {parsed.raw}"
                )
        else:
            evidence.append(evidence_messages.selected_candidate())

        if len(candidates) > 1 and best and best.score - candidates[1].score <= 10:
            warnings.append(evidence_messages.ambiguous_warning())

        release_link = None
        if include_release:
            if parsed.version:
                host_adapter = self._host_adapter(best.host if best else "")
                release_link = self._resolve_release_link(
                    adapter=adapter,
                    parsed=parsed,
                    repository=best,
                    metadata=metadata,
                    host_adapter=host_adapter,
                    warnings=warnings,
                    evidence=evidence,
                )
                if release_link:
                    evidence.append(evidence_messages.resolved_release())
                elif best:
                    warnings.append(evidence_messages.no_release_warning())
                    if self.settings.strict:
                        raise NoReleaseFoundError(f"No release link found for {parsed.raw}")
            else:
                warnings.append(evidence_messages.skipped_release_no_version())
                evidence.append(evidence_messages.skipped_release_no_version())

        return ResolutionResult(
            purl=parsed,
            repository_url=best.normalized_url if best and confidence != "none" else None,
            repository_type=best.repository_type if best and confidence != "none" else None,
            repository_candidates=candidates,
            release_link=release_link,
            confidence=confidence,
            evidence=evidence,
            warnings=warnings,
            metadata_sources=metadata_sources,
        )

    def resolve_repository(self, purl: str) -> ResolutionResult:
        return self.resolve(purl, include_release=False)

    def resolve_release(self, purl: str) -> ResolutionResult:
        result = self.resolve(purl, include_release=True)
        if self.settings.strict and result.release_link is None:
            raise NoReleaseFoundError(f"No release link found for {purl}")
        return result

    def resolve_many(self, purls: Iterable[str]) -> Iterator[ResolutionResult]:
        for purl in purls:
            yield self.resolve(purl)

    def _adapter_for(self, parsed: ParsedPurl) -> EcosystemResolver:
        adapter_cls = ECOSYSTEMS.get(parsed.type)
        if not adapter_cls:
            raise UnsupportedEcosystemError(f"Unsupported package type: {parsed.type}")
        return adapter_cls()

    def _host_adapter(self, host: str) -> HostAdapter | None:
        if not host:
            return None
        return HOSTS.get(host, GENERIC_HOST)

    def _resolve_release_link(
        self,
        *,
        adapter: EcosystemResolver,
        parsed: ParsedPurl,
        repository: RepositoryCandidate | None,
        metadata: Metadata,
        host_adapter: HostAdapter | None,
        warnings: list[str],
        evidence: list[str],
    ) -> ReleaseLink | None:
        if host_adapter is None or not parsed.version:
            return None
        if not self.settings.verify_release_links:
            return adapter.resolve_release_link(parsed, repository, metadata, host_adapter)

        if repository is None:
            return None
        try:
            candidates = host_adapter.candidate_release_links(
                repository.normalized_url,
                parsed.version,
            )
            for candidate in candidates:
                if self.client.url_exists(candidate.url):
                    evidence.append(evidence_messages.verified_release())
                    return candidate
        except MetadataFetchError:
            if self.settings.strict:
                raise
            warnings.append("Could not verify inferred release links")
            return None
        warnings.append(evidence_messages.unverified_release_warning())
        return None

    def _empty_result(
        self,
        parsed: ParsedPurl,
        warnings: list[str],
        evidence: list[str],
        metadata_sources: list[str],
    ) -> ResolutionResult:
        return ResolutionResult(
            purl=parsed,
            repository_url=None,
            repository_type=None,
            repository_candidates=[],
            release_link=None,
            confidence="none",
            evidence=evidence,
            warnings=warnings,
            metadata_sources=metadata_sources,
        )
