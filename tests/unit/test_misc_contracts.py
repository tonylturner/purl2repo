from dataclasses import asdict

from purl2repo.models import ResolverSettings
from purl2repo.resolution.canonicalize import classify_host, normalize_repo_url, url_host
from purl2repo.resolution.evidence import no_release_warning, weak_candidate_warning
from purl2repo.settings import ResolverSettings as ReexportedSettings
from purl2repo.utils.urls import is_repo_like_url
from purl2repo.utils.urls import normalize_repo_url as normalize_util
from purl2repo.utils.versions import preferred_v_tag, version_variants


def test_settings_reexport_and_defaults():
    settings = ResolverSettings()
    assert asdict(settings)["timeout"] == 10.0
    assert settings.user_agent == "purl2repo/2.x"
    assert ReexportedSettings().strict is False


def test_canonicalize_reexports_url_helpers():
    assert (
        normalize_repo_url("git+https://github.com/org/repo.git") == "https://github.com/org/repo"
    )
    assert classify_host("github.com") == "github"
    assert url_host("https://github.com/org/repo") == "github.com"


def test_version_helpers():
    assert version_variants("1.0.0") == ["1.0.0", "v1.0.0"]
    assert version_variants("v1.0.0") == ["v1.0.0", "1.0.0"]
    assert version_variants(" ") == []
    assert preferred_v_tag("1.0.0") == "v1.0.0"
    assert preferred_v_tag("v1.0.0") == "v1.0.0"


def test_misc_url_branches_and_evidence():
    assert normalize_util("https://github.com/org") == "https://github.com/org"
    assert normalize_util("notaurl") is None
    assert normalize_util("https:///missing-host") is None
    assert (
        normalize_util("https://gitlab.com/group/project/tags")
        == "https://gitlab.com/group/project"
    )
    assert normalize_util("https://example.com/org/repo/issues") == "https://example.com/org/repo"
    assert is_repo_like_url("https://github.com/org/repo")
    assert is_repo_like_url("https://example.com/org/repo.git")
    assert no_release_warning().startswith("Repository resolved")
    assert weak_candidate_warning().startswith("Only weak")
