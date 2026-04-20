# Migration From v1

v2 is a clean break from the prototype API. The changes favor a stable public
contract over preserving inconsistent return dictionaries.

## API

Old prototype-style calls should move to the top-level v2 API:

- `get_source_repo_and_release()` -> `resolve()`
- repository-only workflows -> `resolve_repository()`
- release-only workflows -> `resolve_release()`
- batch workflows -> `Resolver(...).resolve_many(...)`

All public functions return typed dataclasses rather than ad hoc dictionaries.

## Repository Fields

The old `github_repo` and `vcs_repo` style fields are replaced by:

- `canonical_repository`: full `RepositoryRef`
- `repository_url`: convenience URL for the canonical repository
- `repository_type`: platform or host classification
- `repository_kind`: source code, artifact hub, VCS, generic, or related kind

Use `canonical_repository` for new integrations. Use `repository_url` only when a
single URL string is enough.

## Version References

`release_link` remains available for compatibility with release-oriented code.
`version_reference` is the broader v2 name because a version-specific link may be
a release, tag, source tree, package page, revision, or registry version.

## Validation

When network is available, v2 validates resolved repository URLs before selecting
the canonical repository. Candidates that verify as missing are discarded. In
`no_network=True`, validation is skipped.

## CLI

The CLI is command-based:

```bash
purl2repo parse <PURL>
purl2repo resolve <PURL>
purl2repo repo <PURL>
purl2repo release <PURL>
```

Use `--json` for the stable machine-readable contract and `--trace` for
candidate scoring details.

## Versionless PURLs

Versionless PURLs are valid in v2. Repository resolution still runs, while
version-specific release or revision resolution is skipped with a warning.

## Evidence And Confidence

Every result includes:

- `confidence`
- `evidence`
- `warnings`
- `metadata_sources`
- `repository_candidates`

Callers should inspect warnings before treating a partial result as complete.
