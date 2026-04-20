from purl2repo.hosts.bitbucket import BitbucketAdapter
from purl2repo.hosts.generic_git import GenericGitAdapter
from purl2repo.hosts.github import GitHubAdapter
from purl2repo.hosts.gitlab import GitLabAdapter


def test_github_release_link_uses_v_prefixed_tag():
    link = GitHubAdapter().infer_release_link("https://github.com/psf/requests", "2.31.0")
    assert link is not None
    assert link.url == "https://github.com/psf/requests/releases/tag/v2.31.0"
    assert link.kind == "release"

    candidates = GitHubAdapter().candidate_release_links(
        "https://github.com/psf/requests",
        "2.31.0",
    )
    assert candidates[0].url.endswith("/releases/tag/2.31.0")
    assert candidates[1].url.endswith("/releases/tag/v2.31.0")
    assert candidates[-1].url.endswith("/tree/v2.31.0")


def test_commit_like_versions_include_commit_links():
    github = GitHubAdapter().infer_release_link(
        "https://github.com/package-url/purl-spec",
        "244fd47e07d1004f0aed9c",
    )
    gitlab = GitLabAdapter().infer_release_link(
        "https://gitlab.com/group/project",
        "244fd47e07d1004f0aed9c",
    )
    bitbucket = BitbucketAdapter().infer_release_link(
        "https://bitbucket.org/org/repo",
        "244fd47e07d1004f0aed9c",
    )

    assert github is not None
    assert github.kind == "commit"
    assert github.url == "https://github.com/package-url/purl-spec/commit/244fd47e07d1004f0aed9c"
    assert gitlab is not None
    assert gitlab.url == "https://gitlab.com/group/project/-/commit/244fd47e07d1004f0aed9c"
    assert bitbucket is not None
    assert bitbucket.url == "https://bitbucket.org/org/repo/commits/244fd47e07d1004f0aed9c"


def test_gitlab_and_bitbucket_release_links():
    gitlab = GitLabAdapter().infer_release_link(
        "https://gitlab.com/group/project/-/tags",
        "1.0.0",
    )
    bitbucket = BitbucketAdapter().infer_release_link(
        "https://bitbucket.org/org/repo/src/main",
        "1.0.0",
    )
    assert gitlab is not None
    assert gitlab.url == "https://gitlab.com/group/project/-/releases/v1.0.0"
    assert bitbucket is not None
    assert bitbucket.url == "https://bitbucket.org/org/repo/src/v1.0.0"


def test_generic_git_does_not_fabricate_release_links():
    adapter = GenericGitAdapter()
    assert adapter.infer_release_link("https://git.example.com/org/repo", "1.0.0") is None
    assert adapter.candidate_release_links("https://git.example.com/org/repo", "1.0.0") == []
