import json

import pytest
from typer.testing import CliRunner

from purl2repo import resolve_repository
from purl2repo.api import Resolver
from purl2repo.cli import app
from purl2repo.errors import NoRepositoryFoundError

runner = CliRunner()


def test_top_level_kwargs_validation():
    with pytest.raises(TypeError, match="Unknown resolver option"):
        resolve_repository("pkg:pypi/requests", unsupported=True)
    with pytest.raises(TypeError, match="timeout"):
        resolve_repository("pkg:pypi/requests", timeout="slow")
    with pytest.raises(TypeError, match="use_cache"):
        resolve_repository("pkg:pypi/requests", use_cache="yes")
    with pytest.raises(TypeError, match="cache_dir"):
        resolve_repository("pkg:pypi/requests", cache_dir=1)
    with pytest.raises(TypeError, match="strict"):
        resolve_repository("pkg:pypi/requests", strict="yes")
    with pytest.raises(TypeError, match="no_network"):
        resolve_repository("pkg:pypi/requests", no_network="yes")
    with pytest.raises(TypeError, match="verify_release_links"):
        resolve_repository("pkg:pypi/requests", verify_release_links="yes")
    with pytest.raises(TypeError, match="user_agent"):
        resolve_repository("pkg:pypi/requests", user_agent=1)


def test_resolver_parse_and_context_close(fake_http_factory):
    fake_http_factory({"https://pypi.org/pypi/requests/json": {"info": {}}})
    with Resolver() as resolver:
        assert resolver.parse_purl("pkg:pypi/requests").name == "requests"


def test_strict_no_repository_raises(fake_http_factory):
    fake_http_factory(
        {"https://pypi.org/pypi/requests/json": {"info": {}}},
        {"https://pypi.org/project/requests/": "<html></html>"},
    )
    with Resolver(strict=True) as resolver, pytest.raises(NoRepositoryFoundError):
        resolver.resolve_repository("pkg:pypi/requests")


def test_cli_human_parse_and_supports():
    parse_result = runner.invoke(app, ["parse", "pkg:pypi/requests"])
    supports_result = runner.invoke(app, ["supports"])

    assert parse_result.exit_code == 0
    assert "type: pypi" in parse_result.stdout
    assert supports_result.exit_code == 0
    assert "Supported ecosystems" in supports_result.stdout


def test_cli_unsupported_and_no_network_exit_codes():
    unsupported = runner.invoke(app, ["resolve", "pkg:gem/rails@1.0.0"])
    no_network = runner.invoke(
        app,
        ["release", "pkg:pypi/requests@1.0.0", "--strict", "--no-network"],
    )

    assert unsupported.exit_code == 3
    assert no_network.exit_code == 5


def test_cli_pretty_json_parse():
    result = runner.invoke(app, ["parse", "pkg:pypi/requests", "--json", "--pretty"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["name"] == "requests"
    assert "\n" in result.stdout
