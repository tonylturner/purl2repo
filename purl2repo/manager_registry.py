from packageurl import PackageURL
from .pypi_parser import PyPiParser
from .npm_parser import NpmParser
from .cargo_parser import CargoParser
from .maven_parser import MavenParser

PARSER_REGISTRY = {
    "pypi": PyPiParser,
    "npm": NpmParser,
    "cargo": CargoParser,
    "maven": MavenParser,
}


def get_source_repo_and_release(purl_str):
    purl = PackageURL.from_string(purl_str)
    parser_cls = PARSER_REGISTRY.get(purl.type)

    if not parser_cls:
        raise ValueError(f"Unsupported package type: {purl.type}")

    parser = parser_cls(purl)
    return parser.get_source_repo_and_release()
