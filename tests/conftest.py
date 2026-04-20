from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from purl2repo.errors import MetadataFetchError

FIXTURES = Path(__file__).parent / "fixtures"


class FakeHttpClient:
    def __init__(
        self,
        json_payloads: dict[str, dict[str, Any]] | None = None,
        text_payloads: dict[str, str] | None = None,
    ):
        self.json_payloads = json_payloads or {}
        self.text_payloads = text_payloads or {}

    def get_json(self, url: str, *, ttl_seconds: int = 3600) -> dict[str, Any]:
        _ = ttl_seconds
        if url not in self.json_payloads:
            if url.startswith("https://api.deps.dev/"):
                raise MetadataFetchError(f"Unexpected deps.dev URL: {url}")
            raise AssertionError(f"Unexpected JSON URL: {url}")
        return self.json_payloads[url]

    def get_text(self, url: str, *, ttl_seconds: int = 3600) -> str:
        _ = ttl_seconds
        if url not in self.text_payloads:
            raise AssertionError(f"Unexpected text URL: {url}")
        return self.text_payloads[url]

    def url_exists(self, url: str, *, ttl_seconds: int = 900) -> bool:
        _ = ttl_seconds
        if "missing" in url or "404" in url:
            return False
        version_like = any(
            marker in url
            for marker in (
                "/releases/",
                "/tags/",
                "/tree/",
                "/commit/",
                "/commits/",
                "/src/",
                "/packages/",
            )
        )
        if version_like:
            return (
                url.endswith("/v2.31.0")
                or url.endswith("/v18.2.0")
                or url.endswith("/v0.8.5")
                or "/commit/" in url
                or "/commits/" in url
                or url.endswith("/tree/main")
                or "/packages/" in url
            )
        return url.startswith(("https://", "http://"))

    def close(self) -> None:
        return None


def load_json(relative: str) -> dict[str, Any]:
    return json.loads((FIXTURES / relative).read_text(encoding="utf-8"))


def load_text(relative: str) -> str:
    return (FIXTURES / relative).read_text(encoding="utf-8")


@pytest.fixture
def fake_http_factory(monkeypatch: pytest.MonkeyPatch):
    def install(
        json_payloads: dict[str, dict[str, Any]] | None = None,
        text_payloads: dict[str, str] | None = None,
    ) -> FakeHttpClient:
        fake = FakeHttpClient(json_payloads, text_payloads)
        monkeypatch.setattr("purl2repo.resolution.engine.HttpClient", lambda settings, cache: fake)
        return fake

    return install
