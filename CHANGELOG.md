# Changelog

All notable changes to this project are documented here. The format follows
Keep a Changelog and the project uses Semantic Versioning.

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
