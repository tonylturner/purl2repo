# CLI

## Commands

- `purl2repo parse <PURL>`: parse and validate a PURL.
- `purl2repo resolve <PURL>`: resolve repository and release information.
- `purl2repo repo <PURL>`: resolve only the repository.
- `purl2repo release <PURL>`: resolve a release or source link with repository context.
- `purl2repo supports`: list ecosystems and host adapters.
- `purl2repo version`: print package version.

## Flags

- `--json`: stable JSON output.
- `--pretty`: pretty JSON output.
- `--strict / --no-strict`: raise on weak or incomplete resolution.
- `--timeout`: HTTP timeout in seconds.
- `--no-cache`: disable memory and disk cache.
- `--cache-dir`: enable disk cache at a specific directory.
- `--verbose`: enable debug logging.
- `--trace`: include candidate scores and reasons in human output.
- `--no-network`: use cache only.
- `--verify-release-links / --no-verify-release-links`: check inferred release
  URLs before returning them.

Release-link verification is disabled by default to avoid extra host requests.
When enabled, `resolve` and `release` check candidate release, tag, and source
URLs in order and return the first reachable URL. If none can be verified,
non-strict mode returns `release_link=null` with a warning; strict mode exits with
a resolution or metadata failure depending on the failure.

Fallback scraping has no CLI flag because it is part of repository resolution.
It only runs when structured metadata does not yield a usable candidate. When it
runs, output includes a warning explaining that fallback scraping was used.

## Exit Codes

- `0`: success
- `2`: invalid input
- `3`: unsupported ecosystem
- `4`: resolution failure
- `5`: network or metadata failure
