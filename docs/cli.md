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
- `--validate-repositories / --no-validate-repositories`: check candidate
  repository URLs before selecting them.
- `--deps-dev-fallback / --no-deps-dev-fallback`: use deps.dev after
  first-party metadata has no usable repository.
- `--scraper-fallback / --no-scraper-fallback`: use bounded HTML scraping after
  structured and deps.dev fallbacks have no usable repository.

Release-link verification is disabled by default to avoid extra host requests.
When enabled, `resolve` and `release` check candidate release, tag, and source
URLs in order and return the first reachable URL. If none can be verified,
non-strict mode returns `release_link=null` with a warning; strict mode exits with
a resolution or metadata failure depending on the failure.

Fallback scraping is enabled by default but only runs when structured metadata
and deps.dev do not yield a usable candidate. Disable it with
`--no-scraper-fallback` for faster, first-party-only inventory runs. Disable
deps.dev with `--no-deps-dev-fallback` when third-party aggregation data is not
desired.

Human output includes `Repository`, `Kind`, `Type`, optional `Version`, release
or revision URL, confidence, evidence, and warnings. JSON output includes the
full `canonical_repository` object, `version_reference` object, and explicit
repository validation fields: `repository_validated` and
`repository_validation_status`.

Example artifact-hub output:

```bash
purl2repo resolve pkg:huggingface/microsoft/deberta-v3-base@main
```

```text
Repository: https://huggingface.co/microsoft/deberta-v3-base
Kind: artifact_hub
Type: huggingface
Version: main
Release: https://huggingface.co/microsoft/deberta-v3-base/tree/main
Confidence: high
```

If a Hugging Face revision cannot be verified, the CLI still reports the
canonical Hugging Face repository and prints `Release: not found`.

Repository URLs are validated during normal networked resolution. If a candidate
verifies as missing, it is discarded and the CLI reports warnings or `Repository:
not found`. `--no-network` skips this validation. `--no-validate-repositories`
also skips validation while still allowing registry metadata fetches.

## Exit Codes

- `0`: success
- `2`: invalid input
- `3`: unsupported ecosystem
- `4`: resolution failure
- `5`: network or metadata failure
