import pytest

from purl2repo import resolve


@pytest.mark.integration
def test_live_npm_react():
    result = resolve("pkg:npm/react")
    assert result.repository_url
