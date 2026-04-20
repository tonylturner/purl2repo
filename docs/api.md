# API

## Top-Level Functions

```python
from purl2repo import parse_purl, resolve, resolve_repository, resolve_release
```

- `parse_purl(purl: str) -> ParsedPurl`
- `resolve_repository(purl: str, **kwargs) -> ResolutionResult`
- `resolve_release(purl: str, **kwargs) -> ResolutionResult`
- `resolve(purl: str, **kwargs) -> ResolutionResult`

Keyword arguments are the `Resolver` settings: `timeout`, `use_cache`,
`cache_dir`, `strict`, `no_network`, `verify_release_links`, and `user_agent`.

## Resolver

```python
from purl2repo import Resolver

resolver = Resolver(timeout=10.0, use_cache=True, strict=False)
result = resolver.resolve("pkg:pypi/requests@2.31.0")
resolver.close()
```

`Resolver.resolve_many(iterable)` reuses the HTTP client and cache.

Set `verify_release_links=True` to require a cached host check before returning
an inferred release link:

```python
resolver = Resolver(verify_release_links=True)
result = resolver.resolve_release("pkg:npm/react@18.2.0")
```

If verification cannot find a reachable release, tag, or source URL, non-strict
mode returns a warning and no release link. Strict mode raises
`NoReleaseFoundError` or `MetadataFetchError` depending on the failure.

## Models

Public models are frozen dataclasses:

- `ParsedPurl`
- `RepositoryRef`
- `RepositoryCandidate`
- `ReleaseLink`
- `ResolutionResult`
- `ResolverSettings`

Each model includes `to_dict()` for JSON-compatible serialization.

`ResolutionResult.canonical_repository` is the first-class repository contract.
It includes `url`, `kind`, `platform`, `host`, `namespace`, `name`,
`is_canonical`, `confidence`, and `reasons`. `repository_url`,
`repository_type`, and `repository_kind` are convenience fields for callers that
do not need the full nested object.

`ResolutionResult.version_reference` mirrors `release_link` and may represent a
release, tag, source tree, package page, revision, or registry version depending
on the PURL type.

Repository kinds are `source_code`, `artifact_hub`, `registry`, `vcs`,
`generic`, and `direct_host`.

## Errors

- `InvalidPurlError`
- `UnsupportedEcosystemError`
- `MetadataFetchError`
- `ResolutionError`
- `NoRepositoryFoundError`
- `NoReleaseFoundError`

In non-strict mode, incomplete repository or release results usually return
warnings instead of exceptions. In strict mode, weak or missing core resolution
states raise explicit exceptions.

Repository URL validation runs when network is available. Candidates that verify
as missing are discarded before `canonical_repository` is selected. In
`no_network=True`, validation is skipped.

## Fallback Scraping

Repository resolution uses structured metadata first. If no usable structured
candidate is found, the resolver may run a bounded fallback scraper against
package/project pages and metadata-provided homepage URLs. Scraped candidates are
returned as repository candidates with `source="scrape"` and reasons that include
source page, extraction method, and score cap. Scraping is not a crawler and does
not run for direct-host PURLs such as GitHub or Bitbucket.

## Tiered PURL Behavior

- PyPI, npm, Cargo, Maven, NuGet, and Go use metadata-backed resolution.
- GitHub and Bitbucket PURLs resolve directly from the PURL path.
- Generic PURLs use `vcs_url`, `repository_url`, then `download_url`.
- Hugging Face PURLs resolve to Hugging Face as the canonical artifact hub.
- Hugging Face revision links are returned only after the `/tree/{revision}` URL
  is verified; otherwise `version_reference` is `None`.
- MLflow PURLs require `registry_url`, `tracking_uri`, or `repository_url`.
