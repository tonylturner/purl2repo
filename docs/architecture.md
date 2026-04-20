# Architecture

`purl2repo` is organized as a compact resolver pipeline.

## Modules

- `purl2repo.purl`: parses, validates, and normalizes Package URLs.
- `purl2repo.models`: stable dataclass contracts used by the API and CLI.
- `purl2repo.api`: public functions and the reusable `Resolver` object.
- `purl2repo.http`: timeout, retry, User-Agent, and cache-aware HTTP access.
- `purl2repo.ecosystems`: registry-specific metadata adapters.
- `purl2repo.hosts`: host-specific repository and release-link behavior.
- `purl2repo.resolution`: orchestration, scoring, evidence, and canonicalization.
- `purl2repo.cli`: Typer command-line interface.

## Data Flow

1. Parse and validate the PURL.
2. Route direct-host, artifact-hub, and generic PURL types before ecosystem
   inference.
3. Select an ecosystem adapter from the PURL type when metadata lookup is needed.
4. Fetch structured registry or module metadata.
5. Extract repository candidates.
6. Normalize repository URLs.
7. Score structured candidates and sort them deterministically.
8. Validate candidate repository URLs when network is available and discard
   candidates that verify as missing.
9. If no usable structured candidate exists, query deps.dev as a third-party,
   lower-confidence fallback for ecosystems covered by Open Source Insights.
10. If deps.dev also yields no usable candidate, run the bounded fallback scraper on
   package/project pages and metadata-provided homepage URLs.
11. Merge fallback candidates back into the candidate set with lower capped
   scores and validate the merged repository URLs.
12. Select the best candidate if confidence is sufficient and build a
   `RepositoryRef`.
13. If a version exists, ask the host adapter or ecosystem adapter for a
   conservative version reference.
   When `verify_release_links=True`, candidate release, tag, and source URLs are
   checked with cached host requests before one is returned.
14. Return a `ResolutionResult` with `canonical_repository`, evidence, warnings,
   metadata sources, and all candidates.

Adapters are intentionally narrow. Adding an ecosystem should not require
changing parser, scoring, CLI, or serialization code beyond adapter registration
and documentation.

deps.dev is intentionally not a primary resolver. Its API can provide package
links, SLSA source repositories, and related project mappings for PyPI, npm,
Cargo, Maven, NuGet, and Go, but those links are third-party aggregation data.
`purl2repo` only asks deps.dev after native ecosystem metadata fails to produce
a usable candidate, validates any returned URL, and caps the score below
first-party registry or POM metadata.

The fallback scraper is not a crawler. It fetches only a small number of
explicitly allowed pages per resolution and does not run for direct repository
PURL types such as GitHub or Bitbucket. Hugging Face PURLs are also excluded from
upstream-source scraping because Hugging Face is treated as canonical for those
artifacts.

The repository model is intentionally broader than Git. A resolved repository can
be source code, an artifact hub, a VCS URL, a registry reference, or a generic
download URL. This prevents GitHub-centric assumptions from leaking into callers
that handle Hugging Face, MLflow, or generic package references.

Repository validation is not a scoring boost. It is a validity check: if a
candidate URL verifies as missing, it is removed from consideration. If
validation cannot run because network is disabled, the resolver preserves the
deterministic result and leaves validation to the caller.
