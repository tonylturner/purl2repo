"""Tiny resolver benchmark for local development."""

from __future__ import annotations

import time

from purl2repo import Resolver

PURLS = [
    "pkg:pypi/requests@2.31.0",
    "pkg:npm/react@18.2.0",
    "pkg:cargo/rand@0.8.5",
]


def main() -> None:
    started = time.perf_counter()
    with Resolver() as resolver:
        results = list(resolver.resolve_many(PURLS))
    elapsed = time.perf_counter() - started
    for result in results:
        print(f"{result.purl.raw}: {result.repository_url} ({result.confidence})")
    print(f"Resolved {len(results)} PURLs in {elapsed:.2f}s")


if __name__ == "__main__":
    main()
