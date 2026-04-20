# Changelog

All notable changes to this project are documented here. The format follows
Keep a Changelog and the project uses Semantic Versioning.

## [Unreleased]

No unreleased changes yet.

## [2.0.2] - 2026-04-20

### Added

- Resolver settings and CLI flags can now disable repository URL validation,
  deps.dev fallback, and scraper fallback for faster bulk inventory workflows.
- `ResolutionResult` now exposes `repository_validated` and
  `repository_validation_status` so callers can read validation state without
  parsing evidence or warning strings.
- `Resolver.resolve_many(..., max_workers=N)` can use a bounded worker pool for
  independent PURL resolution while preserving input order.

### Changed

- Maven parent POM SCM candidates are now scored separately from artifact-owned
  SCM fields and capped below high confidence.
- Scraped fallback candidates without package-specific repository path evidence
  are now capped below the confidence threshold.

### Fixed

- Repository candidates with inconclusive URL validation are no longer allowed
  to remain high confidence.

## [2.0.1] - 2026-04-20

### Added

- Unit tests now vendor and exercise the official upstream purl-spec parse,
  roundtrip, and build examples for every supported PURL type.
- Added a non-gating `scripts/purl_spec_resolution_report.py` helper for
  comparing supported upstream examples against live repository resolution,
  release-link verification, and fallback scraping behavior.
- Added deps.dev as a third-party fallback source for PyPI, npm, Cargo, Maven,
  NuGet, and Go when native ecosystem metadata yields no usable repository.

### Changed

- PURL parsing now follows additional upstream type-specific canonicalization
  examples, including PyPI names, direct-host casing, npm scoped packages,
  subpath trimming, qualifier encoding, and optional slashes after `pkg:`.
- MLflow artifact-hub resolution accepts the upstream `repository_url`
  qualifier in addition to `registry_url` and `tracking_uri`.
- Go module repository inference now survives Go proxy metadata failures when
  the module path itself encodes a repository.
- Go vanity imports now use `go-import` metadata as a bounded fallback before
  lower-confidence third-party sources.
- PyPI version-specific metadata failures now fall back to project-level JSON
  for repository discovery.
- Generic `vcs_url` qualifiers with embedded revision suffixes now normalize to
  the repository URL before validation.
- GitHub, GitLab, and Bitbucket release inference now include commit links for
  commit-like version strings.
- Fallback scraping now filters generic links more conservatively so package
  policy, support, and analysis pages are not treated as repositories.

## [2.0.0] - 2026-04-20

### Added

- Typed public models for parsed PURLs, repository candidates, release links,
  resolver settings, and resolution results.
- Public API functions: `parse_purl`, `resolve`, `resolve_repository`,
  `resolve_release`, and reusable `Resolver`.
- Versionless PURL parsing and repository-only resolution behavior.
- PyPI, npm, Cargo, Maven, NuGet, and Go ecosystem adapters.
- Tiered PURL support for direct-host, generic, and artifact-hub package types.
- `RepositoryRef` and `canonical_repository` output for source code, VCS,
  generic, and artifact-hub repositories.
- Hugging Face artifact hub resolution with verified revision links.
- Direct `pkg:github` and `pkg:bitbucket` resolution without inference.
- Generic PURL qualifier resolution for `vcs_url`, `repository_url`, and
  `download_url`.
- Repository URL validation that discards candidates verified as missing.
- GitHub, GitLab, Bitbucket, and generic git host adapters.
- Scored repository candidates with confidence mapping, evidence, warnings, and
  stable JSON serialization.
- Optional release-link verification with cached host checks.
- Strict fallback HTML scraping for repository recovery when structured metadata
  does not yield a usable candidate.
- Pinned Trivy CLI dependency vulnerability scanning in CI for high and
  critical package vulnerabilities.
- Source distribution manifest that includes the changelog, docs, and project
  support files in release artifacts.
- Typer CLI with parse, resolve, repo, release, supports, and version commands.
- Unit, fixture, and separated live integration test structure.
- PyPI-ready `pyproject.toml`, CI, TestPyPI, and PyPI workflows.

### Changed

- Migrated to a `src/` layout and Python 3.11+ package metadata.
- Expanded runtime support from Python 3.14-only to Python 3.11 and newer.
- Changed runtime version reporting to derive from installed package metadata.
- Replaced ad hoc return dictionaries with stable dataclass contracts.
- Expanded the repository model beyond Git-style source repositories.
- Reworked resolution into parse, fetch, extract, normalize, score, select, and
  release-link stages.
- Changed CLI behavior to explicit subcommands and stable JSON output.

### Fixed

- Version is no longer required for parsing or repository resolution.
- Repository field naming is now consistent across API and CLI output.
- GitHub-only assumptions were replaced by host-aware normalization.
- Hugging Face PURLs are no longer treated as candidates for upstream GitHub
  discovery.
- Unit tests no longer depend on live network calls.

### Removed

- Legacy `setup.py` build path.
- Prototype parser classes with inconsistent method names and return schemas.
- Primary scraping behavior for repository discovery; v2 scraping is a bounded
  fallback only.
