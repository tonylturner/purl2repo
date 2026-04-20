import json

from tests.conftest import load_json
from typer.testing import CliRunner

from purl2repo.cli import app

runner = CliRunner()


def test_cli_parse_json():
    result = runner.invoke(app, ["parse", "pkg:pypi/requests@2.31.0", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["type"] == "pypi"
    assert payload["name"] == "requests"


def test_cli_parse_invalid_exit_code():
    result = runner.invoke(app, ["parse", "pkg:pypi/re%ZZquests"])

    assert result.exit_code == 2


def test_cli_resolve_json_and_trace(fake_http_factory):
    fake_http_factory(
        {
            "https://pypi.org/pypi/requests/2.31.0/json": load_json("pypi/requests.json"),
        }
    )

    result = runner.invoke(app, ["resolve", "pkg:pypi/requests@2.31.0", "--json", "--trace"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["repository_url"] == "https://github.com/psf/requests"
    assert payload["repository_candidates"]


def test_cli_repo_release_supports_and_version(fake_http_factory):
    fake_http_factory(
        {
            "https://pypi.org/pypi/requests/2.31.0/json": load_json("pypi/requests.json"),
        }
    )

    repo = runner.invoke(app, ["repo", "pkg:pypi/requests@2.31.0"])
    release = runner.invoke(app, ["release", "pkg:pypi/requests@2.31.0"])
    supports = runner.invoke(app, ["supports", "--json"])
    version = runner.invoke(app, ["version"])

    assert repo.exit_code == 0
    assert "Repository: https://github.com/psf/requests" in repo.stdout
    assert release.exit_code == 0
    assert "v2.31.0" in release.stdout
    assert supports.exit_code == 0
    assert "pypi" in json.loads(supports.stdout)["ecosystems"]
    assert version.exit_code == 0
    assert version.stdout.strip()
