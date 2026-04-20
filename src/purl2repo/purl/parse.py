"""Package URL parser.

The parser intentionally implements the subset of the Package URL grammar that
matters for resolution while preserving qualifiers and subpaths for callers.
"""

from __future__ import annotations

import re
from urllib.parse import quote, unquote

from purl2repo.errors import InvalidPurlError
from purl2repo.models import ParsedPurl

_TYPE_RE = re.compile(r"^[A-Za-z0-9.+-]+$")
_BAD_PERCENT_RE = re.compile(r"%(?![0-9A-Fa-f]{2})")


def _decode_component(value: str, label: str) -> str:
    if _BAD_PERCENT_RE.search(value):
        raise InvalidPurlError(f"Malformed percent-encoding in {label}.")
    decoded = unquote(value)
    if decoded == "":
        raise InvalidPurlError(f"Empty {label} is not allowed.")
    return decoded


def _parse_qualifiers(query: str | None) -> dict[str, str]:
    if query is None:
        return {}
    if query == "":
        raise InvalidPurlError("Qualifier separator '?' must be followed by key=value pairs.")

    qualifiers: dict[str, str] = {}
    for item in query.split("&"):
        if not item or "=" not in item:
            raise InvalidPurlError("Qualifiers must use key=value syntax.")
        key, value = item.split("=", 1)
        decoded_key = _decode_component(key, "qualifier key").lower()
        decoded_value = _decode_component(value, f"qualifier value for {decoded_key}")
        if decoded_key in qualifiers:
            raise InvalidPurlError(f"Duplicate qualifier key: {decoded_key}")
        qualifiers[decoded_key] = decoded_value
    return qualifiers


def _encode_path_component(value: str) -> str:
    return quote(value, safe=".-_~")


def parse_purl(purl: str) -> ParsedPurl:
    """Parse and validate a Package URL string."""

    if not isinstance(purl, str) or not purl.strip():
        raise InvalidPurlError("PURL must be a non-empty string.")
    raw = purl.strip()
    if not raw.startswith("pkg:"):
        raise InvalidPurlError("PURL must start with 'pkg:'.")

    without_scheme = raw[4:]
    if without_scheme.startswith("//"):
        raise InvalidPurlError("PURL must not contain a URL authority component.")

    main_and_query, sep, subpath_raw = without_scheme.partition("#")
    subpath = _decode_component(subpath_raw, "subpath") if sep else None

    path_part, query_sep, query = main_and_query.partition("?")
    qualifiers = _parse_qualifiers(query if query_sep else None)

    type_part, slash, remainder = path_part.partition("/")
    if not slash:
        raise InvalidPurlError("PURL must include a type and package name separated by '/'.")
    if not type_part or not _TYPE_RE.match(type_part):
        raise InvalidPurlError("PURL type is missing or invalid.")

    package_path, version_sep, version_raw = remainder.partition("@")
    if "@" in version_raw:
        raise InvalidPurlError("PURL contains multiple version separators.")
    version = _decode_component(version_raw, "version") if version_sep else None

    if package_path == "" or package_path.endswith("/") or package_path.startswith("/"):
        raise InvalidPurlError("PURL package path is malformed.")
    parts = [_decode_component(part, "package path component") for part in package_path.split("/")]
    if len(parts) == 1:
        namespace = None
        name = parts[0]
    else:
        namespace = "/".join(parts[:-1])
        name = parts[-1]

    parsed = ParsedPurl(
        raw=raw,
        type=type_part.lower(),
        namespace=namespace,
        name=name,
        version=version,
        qualifiers=dict(sorted(qualifiers.items())),
        subpath=subpath,
    )
    return parsed


def purl_to_string(parsed: ParsedPurl) -> str:
    """Return a canonical string representation for a parsed PURL."""

    path_parts: list[str] = []
    if parsed.namespace:
        path_parts.extend(_encode_path_component(part) for part in parsed.namespace.split("/"))
    path_parts.append(_encode_path_component(parsed.name))
    value = f"pkg:{parsed.type}/{'/'.join(path_parts)}"
    if parsed.version:
        value = f"{value}@{_encode_path_component(parsed.version)}"
    if parsed.qualifiers:
        query = "&".join(
            f"{_encode_path_component(key)}={_encode_path_component(value)}"
            for key, value in sorted(parsed.qualifiers.items())
        )
        value = f"{value}?{query}"
    if parsed.subpath:
        value = f"{value}#{'/'.join(_encode_path_component(p) for p in parsed.subpath.split('/'))}"
    return value
