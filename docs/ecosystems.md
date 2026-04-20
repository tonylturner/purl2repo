# Ecosystems

## PyPI

PyPI uses the JSON API. Versioned PURLs fetch the version-specific JSON endpoint;
versionless PURLs fetch project metadata. Candidate priority is source-like
`project_urls`, then repo-like homepage or download metadata.

If JSON metadata does not produce a usable repository, fallback scraping may
inspect the PyPI project page and metadata-provided URLs.

## npm

npm uses the registry API and supports scoped packages such as
`pkg:npm/%40types/node`. Candidate priority is version-specific `repository`,
package-level `repository`, and repo-like homepage values.

If registry metadata does not produce a usable repository, fallback scraping may
inspect the npm package page and metadata-provided homepage or repository URLs.

## Cargo

Cargo uses crates.io metadata. The resolver prefers the `repository` field and
only uses homepage when it is clearly repository-like. Documentation pages such
as docs.rs are not treated as canonical repositories by themselves.

For versioned Cargo PURLs, repository discovery still uses crate-level metadata
because crates.io version metadata does not consistently include the repository
field.

If crates.io metadata does not produce a usable repository, fallback scraping may
inspect the crates.io crate page and metadata-provided homepage.

## Maven

Maven uses Maven Central POM files. The resolver prefers `scm.url`,
`scm.connection`, and `scm.developerConnection`, then a repo-like project URL.
For versionless Maven PURLs, Maven metadata can identify the latest release POM
for repository discovery, but release-link resolution remains skipped because
the original PURL did not request a version.

If POM SCM metadata does not produce a usable repository, fallback scraping may
inspect the Maven Central artifact page and the POM project URL.
