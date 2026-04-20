import pytest

from purl2repo import resolve


@pytest.mark.integration
def test_live_golang_gin():
    result = resolve("pkg:golang/github.com/gin-gonic/gin@v1.10.0")

    assert result.repository_url == "https://github.com/gin-gonic/gin"
    assert result.repository_kind == "source_code"
    assert result.release_link is not None
