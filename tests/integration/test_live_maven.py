import pytest

from purl2repo import resolve


@pytest.mark.integration
def test_live_maven_log4j():
    result = resolve("pkg:maven/org.apache.logging.log4j/log4j-core@2.22.1")
    assert result.repository_url
