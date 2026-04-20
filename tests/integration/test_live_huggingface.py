import pytest

from purl2repo import resolve


@pytest.mark.integration
def test_live_huggingface_purl_spec_examples():
    revision = "043235d6088ecd3dd5fb5ca3592b6913fd516027"
    distilbert = resolve(f"pkg:huggingface/distilbert-base-uncased@{revision}")
    deberta = resolve(
        "pkg:huggingface/microsoft/deberta-v3-base@559062ad13d311b87b2c455e67dcd5f1c8f65111"
        "?repository_url=https://hub-ci.huggingface.co"
    )

    assert distilbert.repository_url == "https://huggingface.co/distilbert-base-uncased"
    assert distilbert.repository_kind == "artifact_hub"
    assert distilbert.release_link is not None
    assert distilbert.release_link.url.endswith(f"/tree/{revision}")
    assert deberta.repository_url == "https://huggingface.co/microsoft/deberta-v3-base"
    assert deberta.repository_kind == "artifact_hub"
    assert deberta.release_link is not None
    assert "hub-ci.huggingface.co" not in deberta.repository_url
