import json

import httpx
import pytest

from purl2repo.errors import MetadataFetchError
from purl2repo.http.client import HttpClient
from purl2repo.http.retry import backoff_seconds
from purl2repo.models import ResolverSettings
from purl2repo.resolution.cache import ResponseCache


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text="ok"):
        self.status_code = status_code
        self._payload = payload if payload is not None else {"ok": True}
        self.text = text

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            request = httpx.Request("GET", "https://example.com")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError("bad", request=request, response=response)


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def get(self, url):
        self.calls += 1
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def head(self, url):
        self.calls += 1
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def close(self):
        return None


def test_response_cache_memory_and_disk(tmp_path):
    cache = ResponseCache(str(tmp_path))
    cache.set("key", {"value": 1})

    assert cache.get("key", 3600) == {"value": 1}

    disk_cache = ResponseCache(str(tmp_path))
    assert disk_cache.get("key", 3600) == {"value": 1}
    assert disk_cache.get("key", -1) is None


def test_response_cache_ignores_invalid_disk_payload(tmp_path):
    cache = ResponseCache(str(tmp_path))
    cache.set("bad", {"value": 1})
    path = next(tmp_path.iterdir())
    path.write_text("{", encoding="utf-8")

    assert cache.get("bad", 3600) is not None
    assert ResponseCache(str(tmp_path)).get("bad", 3600) is None


def test_http_client_get_json_text_cache_and_close(monkeypatch):
    transport = FakeTransport([FakeResponse(payload={"name": "pkg"}), FakeResponse(text="body")])
    monkeypatch.setattr("purl2repo.http.client.httpx.Client", lambda **kwargs: transport)
    cache = ResponseCache()
    client = HttpClient(ResolverSettings(), cache)

    assert client.get_json("https://example.com/data") == {"name": "pkg"}
    assert client.get_json("https://example.com/data") == {"name": "pkg"}
    assert client.get_text("https://example.com/text") == "body"
    assert client.get_text("https://example.com/text") == "body"
    assert transport.calls == 2
    client.close()


def test_http_client_errors(monkeypatch):
    monkeypatch.setattr(
        "purl2repo.http.client.httpx.Client",
        lambda **kwargs: FakeTransport([FakeResponse(payload=ValueError("no json"))]),
    )
    client = HttpClient(ResolverSettings(), ResponseCache())
    with pytest.raises(MetadataFetchError, match="Invalid JSON"):
        client.get_json("https://example.com/data")

    monkeypatch.setattr(
        "purl2repo.http.client.httpx.Client",
        lambda **kwargs: FakeTransport([FakeResponse(payload=["not", "object"])]),
    )
    client = HttpClient(ResolverSettings(), ResponseCache())
    with pytest.raises(MetadataFetchError, match="Expected JSON object"):
        client.get_json("https://example.com/data")

    client = HttpClient(ResolverSettings(no_network=True), ResponseCache())
    with pytest.raises(MetadataFetchError, match="Network disabled"):
        client.get_text("https://example.com/data")

    client = HttpClient(ResolverSettings(), ResponseCache())
    with pytest.raises(MetadataFetchError, match="non-web"):
        client.get_json("ftp://example.com/data")


def test_http_client_retries_transient_errors(monkeypatch):
    transport = FakeTransport([FakeResponse(status_code=503), FakeResponse(payload={"ok": True})])
    monkeypatch.setattr("purl2repo.http.client.httpx.Client", lambda **kwargs: transport)
    monkeypatch.setattr("purl2repo.http.client.time.sleep", lambda seconds: None)

    client = HttpClient(ResolverSettings(), ResponseCache())

    assert client.get_json("https://example.com/data") == {"ok": True}
    assert transport.calls == 2


def test_http_client_raises_after_http_error(monkeypatch):
    transport = FakeTransport(
        [
            httpx.ConnectError("down"),
            httpx.ConnectError("down"),
            httpx.ConnectError("down"),
        ]
    )
    monkeypatch.setattr("purl2repo.http.client.httpx.Client", lambda **kwargs: transport)
    monkeypatch.setattr("purl2repo.http.client.time.sleep", lambda seconds: None)
    client = HttpClient(ResolverSettings(), ResponseCache())

    with pytest.raises(MetadataFetchError, match="Failed to fetch metadata"):
        client.get_json("https://example.com/data")


def test_http_client_url_exists_cache_get_fallback_and_errors(monkeypatch):
    transport = FakeTransport(
        [
            FakeResponse(status_code=204),
            FakeResponse(status_code=405),
            FakeResponse(status_code=200),
            httpx.ConnectError("down"),
        ]
    )
    monkeypatch.setattr("purl2repo.http.client.httpx.Client", lambda **kwargs: transport)
    cache = ResponseCache()
    client = HttpClient(ResolverSettings(), cache)

    assert client.url_exists("https://example.com/one")
    assert client.url_exists("https://example.com/one")
    assert client.url_exists("https://example.com/two")
    with pytest.raises(MetadataFetchError, match="Failed to verify"):
        client.url_exists("https://example.com/down")

    no_network = HttpClient(ResolverSettings(no_network=True), ResponseCache())
    with pytest.raises(MetadataFetchError, match="Network disabled"):
        no_network.url_exists("https://example.com/missing")
    with pytest.raises(MetadataFetchError, match="non-web"):
        client.url_exists("ftp://example.com/nope")


def test_backoff_seconds_has_jitter(monkeypatch):
    monkeypatch.setattr("purl2repo.http.retry.random.uniform", lambda start, end: 0.05)
    assert backoff_seconds(2, base=0.5, jitter=0.1) == 2.05


def test_disk_cache_payload_is_json(tmp_path):
    cache = ResponseCache(str(tmp_path))
    cache.set("key", {"nested": ["value"]})
    payload = json.loads(next(tmp_path.iterdir()).read_text(encoding="utf-8"))
    assert payload["value"] == {"nested": ["value"]}
