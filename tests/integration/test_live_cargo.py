import pytest

from purl2repo import resolve


@pytest.mark.integration
def test_live_cargo_rand():
    result = resolve("pkg:cargo/rand")
    assert result.repository_url
