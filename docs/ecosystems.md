# Ecosystems

`purl2repo` uses tiered PURL support. Registry and module ecosystems use native
metadata first. Direct-host and artifact-hub PURLs bypass inference because the
PURL itself identifies the canonical repository.

For the full upstream PURL type catalog and purl2repo's support policy, see
[purls.md](purls.md).

For PyPI, npm, Cargo, Maven, NuGet, and Go, deps.dev may be queried as a
third-party fallback when native metadata does not produce a usable repository.
deps.dev candidates are validated and capped below high confidence because they
are aggregation data rather than first-party registry or POM evidence.

## PyPI

PyPI uses the JSON API. Versioned PURLs fetch the version-specific JSON endpoint;
versionless PURLs fetch project metadata. Candidate priority is source-like
`project_urls`, then repo-like homepage or download metadata.

If JSON metadata does not produce a usable repository, deps.dev is tried before
fallback scraping. The scraper may inspect the PyPI project page and
metadata-provided URLs.

## npm

npm uses the registry API and supports scoped packages such as
`pkg:npm/%40types/node`. Candidate priority is version-specific `repository`,
package-level `repository`, and repo-like homepage values.

If registry metadata does not produce a usable repository, deps.dev is tried
before fallback scraping. The scraper may inspect the npm package page and
metadata-provided homepage or repository URLs.

## Cargo

Cargo uses crates.io metadata. The resolver prefers the `repository` field and
only uses homepage when it is clearly repository-like. Documentation pages such
as docs.rs are not treated as canonical repositories by themselves.

For versioned Cargo PURLs, repository discovery still uses crate-level metadata
because crates.io version metadata does not consistently include the repository
field.

If crates.io metadata does not produce a usable repository, deps.dev is tried
before fallback scraping. The scraper may inspect the crates.io crate page and
metadata-provided homepage.

## Maven

Maven uses Maven Central POM files. The resolver prefers `scm.url`,
`scm.connection`, and `scm.developerConnection`, then a repo-like project URL.
For versionless Maven PURLs, Maven metadata can identify the latest release POM
for repository discovery, but release-link resolution remains skipped because
the original PURL did not request a version.

If POM SCM metadata does not produce a usable repository, deps.dev is tried
before fallback scraping. The scraper may inspect the Maven Central artifact
page and the POM project URL.

## NuGet

NuGet uses the registration API. The resolver prefers repository information in
catalog entries, then repo-like project URLs. Versioned NuGet PURLs return a
NuGet package page as the version reference:
`https://www.nuget.org/packages/{name}/{version}`.

If registration metadata does not produce a usable repository, deps.dev is tried
before fallback scraping. The scraper may inspect the NuGet package page and
metadata-provided project URLs.

## Go Modules

Go modules use the Go module proxy for metadata lookup. Repository inference is
based on the module path when it clearly encodes a host-backed repository, such
as `pkg:golang/github.com/gin-gonic/gin@v1.10.0`.

For vanity import domains, the resolver reads `go-import` metadata when the Go
proxy does not provide enough information. If that still fails, deps.dev may be
used as a third-party fallback. The resolver does not crawl arbitrary vanity
domains beyond these bounded metadata checks.

## Direct Repository PURLs

`pkg:github/org/repo@tag` and `pkg:bitbucket/org/repo@tag` resolve directly to
their canonical web repository URLs with high confidence. They do not use
registry inference or fallback scraping.

## Generic PURLs

`pkg:generic` uses explicit qualifiers in priority order:

1. `vcs_url`
2. `repository_url`
3. `download_url`

`vcs_url` and `repository_url` produce `repository_kind="vcs"`. `download_url`
produces `repository_kind="generic"` and is not treated as a canonical source
repository.

When a `vcs_url` includes an embedded revision suffix such as
`git+https://example.org/org/repo@abc123`, the repository URL is normalized
without the revision before validation.

## Artifact Hubs

`pkg:huggingface/{namespace}/{model}@{revision}` resolves to
`https://huggingface.co/{namespace}/{model}` with
`repository_kind="artifact_hub"`. Hugging Face is the canonical repository for
these artifacts; the resolver does not chase GitHub upstream links.

Revision links are conservative. The resolver returns
`https://huggingface.co/{namespace}/{model}/tree/{revision}` only when that URL
can be verified. If verification fails or network is disabled, the repository
still resolves with high confidence and `version_reference` remains `null`.

`pkg:mlflow` is supported when the PURL supplies `registry_url`,
`tracking_uri`, or `repository_url`. The official MLflow PURL examples use
`repository_url`; `purl2repo` treats it as the registry endpoint for artifact-hub
resolution. Without one of those qualifiers, the resolver returns a warning or
raises in strict mode because MLflow has no single public canonical registry.
