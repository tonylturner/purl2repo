import pytest

from purl2repo import resolve


@pytest.mark.integration
def test_live_pypi_requests():
    result = resolve("pkg:pypi/requests")
    assert result.repository_url
