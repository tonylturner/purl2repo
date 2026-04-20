import pytest

from purl2repo import resolve


@pytest.mark.integration
def test_live_nuget_newtonsoft_json():
    result = resolve("pkg:nuget/Newtonsoft.Json@13.0.3")

    assert result.repository_url is not None
    assert result.repository_kind == "source_code"
    assert result.release_link is not None
    assert result.release_link.url == "https://www.nuget.org/packages/Newtonsoft.Json/13.0.3"
