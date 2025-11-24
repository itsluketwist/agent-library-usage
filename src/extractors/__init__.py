"""Library extractors for different programming languages."""

from .base import BaseExtractor
from .csharp import CSharpExtractor
from .go import GoExtractor
from .javascript import JavaScriptExtractor, TypeScriptExtractor
from .python import PythonExtractor
from .rust import RustExtractor


__all__ = [
    "BaseExtractor",
    "PythonExtractor",
    "JavaScriptExtractor",
    "TypeScriptExtractor",
    "GoExtractor",
    "CSharpExtractor",
    "RustExtractor",
    "get_extractor",
    "extract_install_commands",
]


def get_extractor(language: str) -> type[BaseExtractor] | None:
    """
    Get the appropriate extractor class for a given language.

    Returns:
        The extractor class for the language, or None if not found.
    """
    extractor_map = {
        "python": PythonExtractor,
        "javascript": JavaScriptExtractor,
        "typescript": TypeScriptExtractor,
        "go": GoExtractor,
        "rust": RustExtractor,
        "csharp": CSharpExtractor,
    }

    return extractor_map.get(language.lower())


def extract_install_commands(text: str) -> list[tuple[str, str, list[str]]]:
    """
    Extract installation commands from PR body or commit messages.

    Aggregates results from all language-specific extractors.

    Returns:
        List of tuples: (package_manager, command, [packages])
    """
    installations = []

    # Aggregate from all language extractors
    installations.extend(
        PythonExtractor.extract_install_commands(
            text=text,
        )
    )
    installations.extend(
        JavaScriptExtractor.extract_install_commands(
            text=text,
        )
    )
    installations.extend(
        GoExtractor.extract_install_commands(
            text=text,
        )
    )
    installations.extend(
        RustExtractor.extract_install_commands(
            text=text,
        )
    )
    installations.extend(
        CSharpExtractor.extract_install_commands(
            text=text,
        )
    )

    return installations
