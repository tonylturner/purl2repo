import pytest

from purl2repo.utils.urls import classify_host, normalize_repo_url


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("git+https://github.com/org/repo.git", "https://github.com/org/repo"),
        ("git://github.com/org/repo.git", "https://github.com/org/repo"),
        ("ssh://git@github.com/org/repo.git", "https://github.com/org/repo"),
        ("git@github.com:org/repo.git", "https://github.com/org/repo"),
        ("https://github.com/org/repo/issues", "https://github.com/org/repo"),
        ("https://github.com/org/repo/releases", "https://github.com/org/repo"),
        ("https://gitlab.com/group/project/-/tags", "https://gitlab.com/group/project"),
        ("https://bitbucket.org/org/repo/src/master/", "https://bitbucket.org/org/repo"),
        ("https://example.com/org/repo.git", "https://example.com/org/repo"),
    ],
)
def test_normalize_repo_url(raw, expected):
    assert normalize_repo_url(raw) == expected


def test_classify_host():
    assert classify_host("github.com") == "github"
    assert classify_host("gitlab.com") == "gitlab"
    assert classify_host("bitbucket.org") == "bitbucket"
    assert classify_host("git.example.com") == "generic_git"
