# Scoring

Scoring is conservative and explainable. Every `RepositoryCandidate` receives a
numeric score and reasons that are included in API and CLI JSON output.

## Positive Signals

- Direct repository or source field from structured metadata: `+100`
- Maven SCM URL: `+100`
- PyPI `project_urls` labels such as Source, Repository, or Code: `+95`
- Structured homepage that clearly points to a repository root: `+85`
- Scraped fallback link from an allowed HTML page: starts at `+35` and is capped
  at `60`
- Recognized git hosting provider: `+10`
- URL normalizes cleanly to a repository root: `+10`
- Package name appears in the repository path: `+5`

## Negative Signals

- Documentation-only URL: `-25`
- Issue tracker URL that cannot be normalized to a repository root: `-15`
- Organization root without a repository slug: `-40`
- Malformed or unresolvable git syntax: `-100`

## Confidence

- `high`: score >= 90
- `medium`: 65 to 89
- `low`: 35 to 64
- `none`: below 35

If multiple candidates are close in score, the resolver returns all candidates,
chooses the best candidate when confidence remains acceptable, and emits a
warning about plausible alternatives.

Structured metadata wins over scraping because registry APIs and POM fields are
more stable, auditable, and deterministic than arbitrary web pages.

Scraping only runs after structured metadata yields no usable candidate. Scraped
candidates remain visible in the result for explainability, but their score is
capped below clean structured metadata. Whenever scraping is used, the result
includes:

```text
Used fallback scraping because structured metadata did not yield a usable repository candidate
```

Release-link verification is separate from repository confidence. When enabled,
the resolver checks inferred release, tag, and source URLs in host-specific order
and emits evidence when the selected URL exists. Failure to verify a release link
does not reduce repository confidence; it only affects the optional
`release_link` field.
