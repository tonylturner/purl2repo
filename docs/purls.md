# PURL Reference And purl2repo Support

This page explains how `purl2repo` relates to the upstream Package URL (PURL)
specification and which PURL types are supported by the resolver.

## Upstream References

Primary references:

- PURL specification repository: <https://github.com/package-url/purl-spec>
- Type definitions: <https://github.com/package-url/purl-spec/tree/main/types>
- Type documentation: <https://github.com/package-url/purl-spec/tree/main/types-doc>
- Type index: <https://github.com/package-url/purl-spec/blob/main/purl-types-index.json>
- ECMA-427 Package-URL specification: <https://ecma-tc54.github.io/ECMA-427/>
- Package-URL project site: <https://www.packageurl.org/>

The upstream project defines PURL as a standard package identifier with this
shape:

```text
pkg:type/namespace/name@version?qualifiers#subpath
```

`purl2repo` parses the general PURL shape, preserves qualifiers and subpaths, and
then applies resolver-specific behavior by PURL type. Parsing a PURL is broader
than resolving it. A type can be syntactically valid while still unsupported for
repository resolution.

## Supported Types

These types are supported by `purl2repo` today.

| PURL type | Support level | Repository model | Notes |
| --- | --- | --- | --- |
| `pypi` | Full | `source_code` or `generic` | Uses PyPI JSON metadata, structured source fields, fallback scraping. |
| `npm` | Full | `source_code` or `generic` | Uses npm registry metadata and supports scoped packages. |
| `cargo` | Full | `source_code` or `generic` | Uses crates.io metadata. |
| `maven` | Full | `source_code` or `generic` | Uses Maven Central POM and SCM fields. |
| `nuget` | Full | `source_code` or `generic` | Uses NuGet registration metadata. Version references point to NuGet package pages. |
| `golang` | Full | `source_code` or `generic` | Uses Go module proxy metadata and module-path inference. |
| `github` | Direct | `source_code` | PURL encodes the repository directly. No inference or scraping. |
| `bitbucket` | Direct | `source_code` | PURL encodes the repository directly. No inference or scraping. |
| `generic` | Explicit | `vcs` or `generic` | Uses `vcs_url`, then `repository_url`, then `download_url` qualifiers. |
| `huggingface` | Artifact hub | `artifact_hub` | Hugging Face is canonical. GitHub upstream links are not chased. Revision links are returned only after verification. |
| `mlflow` | Artifact hub | `artifact_hub` | Requires `registry_url` or `tracking_uri`; no single public canonical registry exists. |

## Registered Upstream Types

The upstream PURL type index currently includes these registered types:

```text
alpm, apk, bazel, bitbucket, bitnami, cargo, chrome-extension, cocoapods,
composer, conan, conda, cpan, cran, deb, docker, gem, generic, github, golang,
hackage, hex, huggingface, julia, luarocks, maven, mlflow, npm, nuget, oci,
opam, otp, pub, pypi, qpkg, rpm, swid, swift, vscode-extension, yocto
```

`purl2repo` does not claim resolution support for every registered type. Its
goal is canonical repository resolution, not package download, vulnerability
analysis, SBOM storage, or artifact mirroring.

## Support Categories

### Full Metadata-Backed Resolution

These types have registry or ecosystem adapters:

- `pypi`
- `npm`
- `cargo`
- `maven`
- `nuget`
- `golang`

They support metadata lookup, repository candidate extraction, scoring,
validation, confidence, evidence, and best-effort version references.

### Direct Repository Resolution

These types directly encode a source repository:

- `github`
- `bitbucket`

They bypass ecosystem inference. The repository URL is derived directly from the
PURL path and validated when network is available.

### Explicit Generic Resolution

`generic` has no universal registry. `purl2repo` supports it only when the PURL
contains explicit URL qualifiers:

1. `vcs_url`
2. `repository_url`
3. `download_url`

This keeps behavior deterministic and avoids guessing from package names.

### Artifact Hub Resolution

These types model artifact hubs rather than upstream source-code repositories:

- `huggingface`
- `mlflow`

For Hugging Face, the Hub repository is canonical:

```text
pkg:huggingface/microsoft/deberta-v3-base@559062ad13d311b87b2c455e67dcd5f1c8f65111
```

resolves to:

```text
https://huggingface.co/microsoft/deberta-v3-base
```

The version reference is returned only when the Hugging Face revision URL exists.

For MLflow, callers must provide a registry location through `registry_url` or
`tracking_uri`.

## Good Future Targets

These types are good candidates for future support because they usually have
structured metadata that can expose source repository information:

| PURL type | Why it is a plausible target |
| --- | --- |
| `composer` | Packagist exposes package metadata with repository/source fields. |
| `gem` | RubyGems metadata often includes source code and homepage links. |
| `hex` | Hex packages often link to source repositories. |
| `pub` | pub.dev metadata commonly includes repository and homepage fields. |
| `swift` | Swift Package Index and package manifests can expose repository identity. |
| `cocoapods` | Podspec metadata can include source and homepage information. |
| `conan` | Conan Center recipes may expose source and homepage links. |
| `conda` | Conda-forge recipe metadata may expose upstream source and feedstock repos. |
| `cran` | CRAN package metadata can expose URLs, but source repo confidence varies. |
| `cpan` | CPAN metadata can expose repository links for many distributions. |
| `hackage` | Hackage package metadata may include source repository links. |
| `julia` | Julia package registry metadata maps packages to Git repositories. |
| `luarocks` | Rockspecs can include source and homepage references. |
| `opam` | OPAM package metadata frequently includes source and dev repository URLs. |
| `otp` | Erlang/OTP package metadata may be resolvable through Hex-style sources when available. |
| `vscode-extension` | Marketplace metadata can include repository links for many extensions. |
| `chrome-extension` | Chrome Web Store packages may include homepages, but source links are inconsistent. |

Future support should require:

- a stable structured metadata source
- deterministic package lookup
- source or artifact repository fields that can be validated
- tests that do not depend on scraping as the primary path

## Probably Out Of Scope Or Limited Support

Some PURL types are valid identifiers but do not naturally answer “what is the
canonical source repository?” in a deterministic way.

| PURL type | Why support is limited |
| --- | --- |
| `alpm`, `apk`, `deb`, `rpm`, `qpkg` | Distro packages often represent repackaged source plus downstream patches. The distro package repository, upstream source repository, and source package archive can all be different. |
| `docker`, `oci` | Container images are artifact registry objects. Source repositories are usually labels or external metadata, not guaranteed by the artifact identity. |
| `bitnami` | Bitnami artifacts may wrap upstream software; canonical source can differ from the packaged artifact source. |
| `yocto` | Recipes may point to source archives, mirrors, or patch sets; repository identity is recipe-specific. |
| `swid` | SWID identifies software inventory tags, not a package registry with source repository metadata. |
| `bazel` | Bazel module and workspace naming can be repository-backed, but there is no universal resolver without a specific registry strategy. |

These types may still be useful future targets for artifact-hub or registry
models, but they should not be forced into source-code repository semantics.

## Unsupported Types

All registered upstream types not listed in [Supported Types](#supported-types)
are currently unsupported for repository resolution.

Unsupported does not mean invalid. `parse_purl()` can still parse valid PURLs
from unsupported types. `resolve()` raises `UnsupportedEcosystemError` unless the
type is one of the supported direct, generic, artifact-hub, or registry-backed
types above.

## Resolver Policy

`purl2repo` follows these rules:

- Unknown is better than confidently wrong.
- Structured metadata wins over scraping.
- Direct repository PURLs bypass inference.
- Artifact hubs are repositories when the artifact lives there.
- Repository URLs are validated when network is available.
- A 404 repository URL is not returned as canonical.
- Version references are best effort and may be absent even when the repository
  is resolved with high confidence.
