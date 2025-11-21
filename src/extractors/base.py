"""Base extractor class with common functionality."""

import re
from typing import List, Optional, Tuple


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

        Returns:
            List of tuples: (package_manager, command, [packages])
            Examples:
                [("pip", "install", ["numpy", "pandas"]),
                 ("npm", "install", ["react", "lodash"])]
        """
        installations = []

        # Python: pip install, pip3 install, python -m pip install
        pip_pattern = re.compile(
            r"(?:pip|pip3|python3?\s+-m\s+pip)\s+install\s+([^\n]+)", re.IGNORECASE
        )
        for match in pip_pattern.finditer(text):
            packages_str = match.group(1)
            # Remove common flags (single dash followed by single letter)
            packages_str = re.sub(r"\s-[a-zA-Z]\s+\S+", " ", packages_str)
            packages_str = re.sub(r"\s-[a-zA-Z](?:\s|$)", " ", packages_str)
            # Remove long flags (double dash)
            # Only handle --flag and --flag=value, not --flag value (ambiguous with package names)
            packages_str = re.sub(
                r"\s--[a-z][a-z0-9-]*(?:=\S+)?(?:\s|$)", " ", packages_str
            )
            # Split and clean
            packages = [
                p.strip()
                for p in packages_str.split()
                if p.strip() and not p.startswith("-") and p != "."
            ]
            if packages:
                installations.append(("pip", "install", packages))

        # Node.js: npm install, yarn add, pnpm add
        npm_pattern = re.compile(
            r"(npm|yarn|pnpm)\s+(install|add|i)\s+([^\n]+)", re.IGNORECASE
        )
        for match in npm_pattern.finditer(text):
            pkg_manager = match.group(1).lower()
            packages_str = match.group(3)
            # Remove flags (single dash followed by single letter)
            packages_str = re.sub(r"\s-[a-zA-Z]\s+\S+", " ", packages_str)
            packages_str = re.sub(r"\s-[a-zA-Z](?:\s|$)", " ", packages_str)
            # Remove long flags (double dash)
            packages_str = re.sub(r"\s--[a-z-]+(?:=\S+)?(?:\s|$)", " ", packages_str)
            # Split and clean
            packages = [
                p.strip()
                for p in packages_str.split()
                if p.strip()
                and not p.startswith("-")
                and p not in ["install", "add", "i"]
            ]
            if packages:
                installations.append((pkg_manager, "install", packages))

        # Go: go get, go install
        go_pattern = re.compile(r"go\s+(get|install)\s+([^\n]+)", re.IGNORECASE)
        for match in go_pattern.finditer(text):
            command = match.group(1).lower()
            packages_str = match.group(2)
            # Remove flags (single dash followed by letter)
            packages_str = re.sub(r"\s-[a-zA-Z](?:\s|$)", " ", packages_str)
            packages_str = re.sub(r"\s-[a-zA-Z]\s+\S+", " ", packages_str)
            # Split and clean
            packages = [
                p.strip()
                for p in packages_str.split()
                if p.strip() and not p.startswith("-")
            ]
            if packages:
                installations.append(("go", command, packages))

        return installations
