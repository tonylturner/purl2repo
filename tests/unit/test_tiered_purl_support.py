import json

from typer.testing import CliRunner

from purl2repo import Resolver, resolve
from purl2repo.cli import app
from purl2repo.ecosystems.golang import GoResolver
from purl2repo.ecosystems.nuget import NuGetResolver
from purl2repo.errors import MetadataFetchError, NoRepositoryFoundError
from purl2repo.purl.parse import parse_purl

runner = CliRunner()


def test_huggingface_resolves_as_canonical_artifact_hub_without_network():
    with Resolver(no_network=True) as resolver:
        result = resolver.resolve("pkg:huggingface/microsoft/deberta-v3-base@abc123")

    assert result.repository_url == "https://huggingface.co/microsoft/deberta-v3-base"
    assert result.repository_kind == "artifact_hub"
    assert result.repository_type == "huggingface"
    assert result.canonical_repository is not None
    assert result.canonical_repository.kind == "artifact_hub"
    assert result.canonical_repository.platform == "huggingface"
    assert result.release_link is None
    assert result.version_reference is None
    assert "Could not verify Hugging Face revision link" in result.warnings[0]
    assert result.confidence == "high"


def test_huggingface_verified_revision_link(fake_http_factory):
    fake = fake_http_factory()
    fake.url_exists = lambda url, ttl_seconds=900: (
        url == "https://huggingface.co/microsoft/deberta-v3-base" or url.endswith("/tree/main")
    )

    result = resolve("pkg:huggingface/microsoft/deberta-v3-base@main")

    assert result.release_link is not None
    assert result.release_link.kind == "revision"
    assert result.release_link.url == ("https://huggingface.co/microsoft/deberta-v3-base/tree/main")
    assert "Verified Hugging Face revision link exists" in result.evidence


def test_huggingface_unverified_revision_returns_repository_only(fake_http_factory):
    fake = fake_http_factory()
    fake.url_exists = lambda url, ttl_seconds=900: (
        url == "https://huggingface.co/microsoft/deberta-v3-base"
    )

    result = resolve("pkg:huggingface/microsoft/deberta-v3-base@abc123")

    assert result.repository_url == "https://huggingface.co/microsoft/deberta-v3-base"
    assert result.release_link is None
    assert result.version_reference is None
    assert "could not be verified" in result.warnings[0]


def test_huggingface_purl_spec_examples_keep_hub_canonical(fake_http_factory):
    revision = "043235d6088ecd3dd5fb5ca3592b6913fd516027"
    fake = fake_http_factory()
    fake.url_exists = lambda url, ttl_seconds=900: (
        url == "https://huggingface.co/distilbert-base-uncased"
        or url == "https://huggingface.co/microsoft/deberta-v3-base"
        or url.endswith(f"/tree/{revision}")
    )

    distilbert = resolve(f"pkg:huggingface/distilbert-base-uncased@{revision}")
    deberta = resolve(
        "pkg:huggingface/microsoft/deberta-v3-base@559062ad13d311b87b2c455e67dcd5f1c8f65111"
        "?repository_url=https://hub-ci.huggingface.co"
    )

    assert distilbert.repository_url == "https://huggingface.co/distilbert-base-uncased"
    assert distilbert.release_link is not None
    assert distilbert.release_link.url == (
        f"https://huggingface.co/distilbert-base-uncased/tree/{revision}"
    )
    assert deberta.repository_url == "https://huggingface.co/microsoft/deberta-v3-base"
    assert deberta.canonical_repository is not None
    assert deberta.canonical_repository.platform == "huggingface"


def test_huggingface_json_uses_expanded_repository_contract():
    result = runner.invoke(
        app,
        [
            "resolve",
            "pkg:huggingface/microsoft/deberta-v3-base@abc123",
            "--json",
            "--no-network",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["canonical_repository"]["url"] == (
        "https://huggingface.co/microsoft/deberta-v3-base"
    )
    assert payload["canonical_repository"]["kind"] == "artifact_hub"
    assert payload["canonical_repository"]["platform"] == "huggingface"
    assert payload["repository_kind"] == "artifact_hub"
    assert payload["version_reference"] is None


def test_huggingface_cli_human_output_includes_kind_and_version():
    result = runner.invoke(
        app,
        ["resolve", "pkg:huggingface/microsoft/deberta-v3-base@abc123", "--no-network"],
    )

    assert result.exit_code == 0
    assert "Repository: https://huggingface.co/microsoft/deberta-v3-base" in result.stdout
    assert "Kind: artifact_hub" in result.stdout
    assert "Release: not found" in result.stdout
    assert "Confidence: high" in result.stdout


def test_direct_host_purls_bypass_inference_and_resolve_high_confidence():
    github = resolve("pkg:github/package-url/purl-spec@v1.0.0", no_network=True)
    bitbucket = resolve("pkg:bitbucket/team/repo@1.2.3", no_network=True)

    assert github.repository_url == "https://github.com/package-url/purl-spec"
    assert github.repository_kind == "source_code"
    assert github.repository_candidates[0].source == "direct_host"
    assert github.confidence == "high"
    assert github.release_link is not None
    assert github.release_link.source == "github"
    assert bitbucket.repository_url == "https://bitbucket.org/team/repo"
    assert bitbucket.repository_kind == "source_code"
    assert bitbucket.release_link is not None
    assert bitbucket.release_link.source == "bitbucket"


def test_direct_host_versionless_and_missing_namespace_paths():
    versionless = resolve("pkg:github/package-url/purl-spec", no_network=True)
    missing_namespace = resolve("pkg:github/repo", no_network=True)

    assert versionless.release_link is None
    assert "Version not supplied" in versionless.warnings[0]
    assert missing_namespace.repository_url is None
    assert missing_namespace.confidence == "none"


def test_direct_host_404_repository_is_not_valid(fake_http_factory):
    fake = fake_http_factory()
    fake.url_exists = lambda url, ttl_seconds=900: False

    result = resolve("pkg:github/org/missing@1.0.0")

    assert result.repository_url is None
    assert result.confidence == "none"
    assert "did not validate" in result.warnings[0]


def test_registry_404_repository_candidate_is_discarded(fake_http_factory):
    fake_http_factory(
        {
            "https://pypi.org/pypi/demo/json": {
                "info": {"project_urls": {"Source": "https://github.com/org/missing"}}
            }
        },
        {
            "https://pypi.org/project/demo/": "",
            "https://github.com/org/missing": "",
        },
    )

    result = resolve("pkg:pypi/demo")

    assert result.repository_url is None
    assert result.repository_candidates == []
    assert any("did not validate" in warning for warning in result.warnings)


def test_generic_uses_vcs_url_before_other_url_qualifiers():
    purl = (
        "pkg:generic/example@1.0.0?"
        "repository_url=https://example.com/project&"
        "vcs_url=git+https://github.com/org/repo.git&"
        "download_url=https://downloads.example.com/archive.tgz"
    )

    result = resolve(purl, no_network=True)

    assert result.repository_url == "https://github.com/org/repo"
    assert result.repository_kind == "vcs"
    assert result.canonical_repository is not None
    assert result.canonical_repository.platform == "github"
    assert result.metadata_sources == ["generic-purl-qualifiers"]


def test_generic_vcs_url_strips_embedded_revision():
    result = resolve(
        "pkg:generic/bitwarderl?vcs_url=git%2Bhttps://git.fsfe.org/dxtr/bitwarderl%40cc55108da32",
        no_network=True,
    )

    assert result.repository_url == "https://git.fsfe.org/dxtr/bitwarderl"
    assert result.repository_kind == "vcs"


def test_generic_repository_download_and_missing_qualifier_paths():
    repository = resolve(
        "pkg:generic/example?repository_url=https://gitlab.com/group/project",
        no_network=True,
    )
    download = resolve(
        "pkg:generic/example@1.0.0?download_url=https://downloads.example.com/archive.tgz",
        no_network=True,
    )
    missing = resolve("pkg:generic/example", no_network=True)

    assert repository.repository_kind == "vcs"
    assert repository.release_link is None
    assert "Version not supplied" in repository.warnings[0]
    assert download.repository_kind == "generic"
    assert download.canonical_repository is not None
    assert download.canonical_repository.is_canonical is False
    assert missing.repository_url is None
    assert missing.confidence == "none"


def test_mlflow_artifact_hub_paths():
    resolved = resolve(
        "pkg:mlflow/team/model@7?registry_url=https://mlflow.example.com",
        no_network=True,
    )
    repository_url = resolve(
        "pkg:mlflow/trafficsigns@10?"
        "model_uuid=36233173b22f4c89b451f1228d700d49&"
        "run_id=410a3121-2709-4f88-98dd-dba0ef056b0a&"
        "repository_url=https://adb-5245952564735461.0.azuredatabricks.net/api/2.0/mlflow",
        no_network=True,
    )
    missing = resolve("pkg:mlflow/team/model", no_network=True)

    assert resolved.repository_kind == "artifact_hub"
    assert resolved.repository_type == "mlflow"
    assert resolved.release_link is not None
    assert resolved.release_link.kind == "version"
    assert repository_url.repository_url == (
        "https://adb-5245952564735461.0.azuredatabricks.net/api/2.0/mlflow"
    )
    assert repository_url.release_link is not None
    assert repository_url.purl.name == "trafficsigns"
    assert missing.repository_url is None

    with Resolver(strict=True, no_network=True) as resolver:
        try:
            resolver.resolve("pkg:mlflow/team/model")
        except NoRepositoryFoundError as exc:
            assert "MLflow registry URL" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("strict MLflow resolution should fail")


def test_nuget_registry_resolution(fake_http_factory):
    fake_http_factory(
        {
            "https://api.nuget.org/v3/registration5-semver1/newtonsoft.json/index.json": {
                "items": [
                    {
                        "items": [
                            {
                                "catalogEntry": {
                                    "repository": {
                                        "url": "https://github.com/JamesNK/Newtonsoft.Json"
                                    },
                                    "projectUrl": "https://www.newtonsoft.com/json",
                                }
                            }
                        ]
                    }
                ]
            }
        }
    )

    result = resolve("pkg:nuget/Newtonsoft.Json@13.0.3")

    assert result.repository_url == "https://github.com/JamesNK/Newtonsoft.Json"
    assert result.repository_kind == "source_code"
    assert result.release_link is not None
    assert result.release_link.url == "https://www.nuget.org/packages/Newtonsoft.Json/13.0.3"
    assert result.metadata_sources == ["nuget-registration"]


def test_nuget_adapter_catalog_shapes_and_fallback_pages():
    adapter = NuGetResolver()
    parsed = parse_purl("pkg:nuget/Demo@1.0.0")
    metadata = {
        "items": [
            {"catalogEntry": {"repositoryUrl": "https://github.com/org/root"}},
            {
                "items": [
                    {
                        "catalogEntry": {
                            "projectUrl": "https://docs.example.com/demo",
                            "repository": {"url": "https://gitlab.com/org/demo"},
                        }
                    },
                    {"catalogEntry": {"projectUrl": "https://github.com/org/demo"}},
                ]
            },
        ],
        "catalogEntry": {"repositoryUrl": "https://bitbucket.org/org/demo"},
    }

    candidates = adapter.extract_candidates(parsed, metadata)
    pages = adapter.fallback_scrape_pages(parsed, metadata)
    no_release = adapter.resolve_release_link(
        parse_purl("pkg:nuget/Demo"),
        None,
        {},
        None,
    )

    assert [candidate.normalized_url for candidate in candidates] == [
        "https://github.com/org/root",
        "https://gitlab.com/org/demo",
        "https://github.com/org/demo",
        "https://bitbucket.org/org/demo",
    ]
    assert pages == [
        "https://www.nuget.org/packages/Demo",
        "https://docs.example.com/demo",
        "https://github.com/org/demo",
    ]
    assert no_release is None


def test_golang_module_path_resolution(fake_http_factory):
    fake_http_factory(
        {
            "https://proxy.golang.org/github.com/gin-gonic/gin/@v/v1.10.0.info": {
                "Version": "v1.10.0",
                "Time": "2024-05-07T13:47:00Z",
            }
        }
    )

    result = resolve("pkg:golang/github.com/gin-gonic/gin@v1.10.0")

    assert result.repository_url == "https://github.com/gin-gonic/gin"
    assert result.repository_kind == "source_code"
    assert result.repository_candidates[0].source == "module_path"
    assert result.release_link is not None
    assert result.release_link.source == "github"


def test_golang_module_path_survives_proxy_metadata_failure(fake_http_factory):
    fake = fake_http_factory()
    fake.get_json = lambda url, ttl_seconds=3600: (_ for _ in ()).throw(
        MetadataFetchError(f"down: {url}")
    )

    result = resolve("pkg:golang/github.com/gorilla/context@234fd47e07d1004f0aed9c")

    assert result.repository_url == "https://github.com/gorilla/context"
    assert result.repository_kind == "source_code"
    assert result.release_link is not None
    assert result.release_link.kind == "commit"
    assert any("go-module-proxy" in warning for warning in result.warnings)


def test_golang_vanity_import_metadata_prefers_source_repo(fake_http_factory):
    fake_http_factory(
        {
            "https://proxy.golang.org/google.golang.org/genproto/@latest": {
                "Version": "v0.0.1",
            }
        },
        {
            "https://google.golang.org/genproto?go-get=1": (
                '<meta name="go-import" '
                'content="google.golang.org/genproto git '
                'https://github.com/googleapis/go-genproto">'
            )
        },
    )

    result = resolve("pkg:golang/google.golang.org/genproto")

    assert result.repository_url == "https://github.com/googleapis/go-genproto"
    assert result.repository_candidates[0].source == "go_import_meta"


def test_golang_latest_and_module_path_helpers(fake_http_factory):
    fake_http_factory(
        {
            "https://proxy.golang.org/example.com/mod/@latest": {
                "Version": "v0.1.0",
            }
        },
        {
            "https://example.com/mod?go-get=1": "<html></html>",
        },
    )

    result = resolve("pkg:golang/example.com/mod")
    adapter = GoResolver()

    assert result.repository_url == "https://example.com/mod"
    assert result.release_link is None
    assert adapter.extract_candidates(parse_purl("pkg:golang/demo"), {"module_path": 1}) == []


def test_supports_lists_tiered_purl_types():
    result = runner.invoke(app, ["supports", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert "nuget" in payload["ecosystems"]
    assert "golang" in payload["ecosystems"]
    assert "huggingface" in payload["purl_types"]
    assert "github" in payload["purl_types"]
