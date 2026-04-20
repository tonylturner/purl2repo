"""Supported ecosystem adapters."""

from .cargo import CargoResolver
from .maven import MavenResolver
from .npm import NpmResolver
from .pypi import PyPiResolver

__all__ = ["CargoResolver", "MavenResolver", "NpmResolver", "PyPiResolver"]
