"""Base extractor class with common functionality."""

import re
from typing import Dict, List, Optional, Tuple


class BaseExtractor:
    """Base class for language-specific extractors."""

    # Version specification patterns
    VERSION_PATTERN = re.compile(r"([=<>!~]+)?\s*(\d+(?:\.\d+)*(?:\.\*)?)")

    @staticmethod
    def has_version_spec(version_str: Optional[str]) -> bool:
        """Check if a version string contains a version specification."""
        if not version_str:
            return False
        return bool(BaseExtractor.VERSION_PATTERN.search(version_str))

    @staticmethod
    def extract_version_operator(version_str: str) -> Optional[str]:
        """Extract the version operator (e.g., ==, >=, ~, ^) from version string."""
        operators = ["==", ">=", "<=", ">", "<", "~=", "!=", "^", "~"]
        for op in operators:
            if op in version_str:
                return op
        return None

    @staticmethod
    def extract_install_commands(text: str) -> List[Tuple[str, str, List[str]]]:
        """
        Extract installation commands from PR body or commit messages.

        This base implementation returns an empty list. Language-specific extractors
        should override this method with their own installation command patterns.

        Returns:
            List of tuples: (package_manager, command, [packages])
        """
        raise NotImplementedError()

    @staticmethod
    def extract_from_file(filename: str, content: str) -> Dict[str, Optional[str]]:
        """
        Extract libraries from a file based on its type.

        This method should be overridden by language-specific extractors to handle
        their own file type detection and extraction logic.

        Returns:
            Dictionary mapping library names to their version specifications (if available).
            For code files, version will be None. For dependency files, version will be the specified version.
        """
        raise NotImplementedError()
