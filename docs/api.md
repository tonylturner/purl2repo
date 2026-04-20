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
- `RepositoryCandidate`
- `ReleaseLink`
- `ResolutionResult`
- `ResolverSettings`

Each model includes `to_dict()` for JSON-compatible serialization.

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

## Fallback Scraping

Repository resolution uses structured metadata first. If no usable structured
candidate is found, the resolver may run a bounded fallback scraper against
package/project pages and metadata-provided homepage URLs. Scraped candidates are
returned as repository candidates with `source="scrape"` and reasons that include
source page, extraction method, and score cap. Scraping is not a crawler and does
not run for direct-host PURLs such as GitHub or Bitbucket.
