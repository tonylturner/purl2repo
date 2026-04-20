"""Local smoke test for installed purl2repo package."""

from __future__ import annotations

from purl2repo import parse_purl


def main() -> None:
    parsed = parse_purl("pkg:pypi/requests@2.31.0")
    assert parsed.type == "pypi"
    assert parsed.name == "requests"
    print("purl2repo smoke test passed")


if __name__ == "__main__":
    main()
