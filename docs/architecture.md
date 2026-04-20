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
2. Select an ecosystem adapter from the PURL type.
3. Fetch structured registry metadata.
4. Extract repository candidates.
5. Normalize repository URLs.
6. Score structured candidates and sort them deterministically.
7. If no usable structured candidate exists, run the bounded fallback scraper on
   package/project pages and metadata-provided homepage URLs.
8. Merge scraped candidates back into the candidate set with lower capped scores.
9. Select the best candidate if confidence is sufficient.
10. If a version exists, ask the host adapter for a conservative release link.
   When `verify_release_links=True`, candidate release, tag, and source URLs are
   checked with cached host requests before one is returned.
11. Return a `ResolutionResult` with evidence, warnings, metadata sources, and all
   candidates.

Adapters are intentionally narrow. Adding an ecosystem should not require
changing parser, scoring, CLI, or serialization code beyond adapter registration
and documentation.

The fallback scraper is not a crawler. It fetches only a small number of
explicitly allowed pages per resolution and does not run for direct repository
PURL types such as GitHub or Bitbucket. Hugging Face PURLs are also excluded from
upstream-source scraping because Hugging Face is treated as canonical for those
artifacts.
