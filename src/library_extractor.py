"""
Library extractor - backwards compatibility layer.

This module provides backwards compatibility by importing from the new
extractors submodule structure.
"""

# Import everything from the new structure for backwards compatibility
from .extractors.library_extractor import LibraryExtractor


__all__ = ["LibraryExtractor"]
