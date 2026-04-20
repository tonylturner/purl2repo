"""Go module adapter."""

from __future__ import annotations

from urllib.parse import quote

from purl2repo.ecosystems.base import EcosystemResolver, Metadata, dedupe_candidates, make_candidate
from purl2repo.http.client import HttpClient
from purl2repo.models import ParsedPurl, RepositoryCandidate
from purl2repo.utils.urls import is_repo_like_url


class GoResolver(EcosystemResolver):
    ecosystem = "golang"
    metadata_source = "go-module-proxy"

    def fetch_metadata(self, parsed: ParsedPurl, client: HttpClient) -> Metadata:
        module_path = go_module_path(parsed)
        escaped = quote(module_path, safe="/")
        if parsed.version:
            url = f"https://proxy.golang.org/{escaped}/@v/{parsed.version}.info"
        else:
            url = f"https://proxy.golang.org/{escaped}/@latest"
        return {
            "module_path": module_path,
            "proxy_info": client.get_json(url),
        }

    def extract_candidates(
        self, parsed: ParsedPurl, metadata: Metadata
    ) -> list[RepositoryCandidate]:
        module_path = metadata.get("module_path")
        if not isinstance(module_path, str):
            module_path = go_module_path(parsed)
        candidates: list[RepositoryCandidate | None] = []
        if is_repo_like_url(module_path):
            candidates.append(
                make_candidate(
                    module_path,
                    "module_path",
                    "Candidate inferred from Go module path",
                )
            )
        return dedupe_candidates(candidates)


def go_module_path(parsed: ParsedPurl) -> str:
    return f"{parsed.namespace}/{parsed.name}" if parsed.namespace else parsed.name
