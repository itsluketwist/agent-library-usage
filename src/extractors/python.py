"""Python library extraction logic."""

import re
import sys
from typing import Dict, List, Literal, Optional, Set, Tuple

from .base import BaseExtractor


class PythonExtractor(BaseExtractor):
    """Extract libraries from Python code and dependency files."""

    # Python import pattern
    IMPORT_PATTERN = re.compile(
        pattern=r"^(?:from\s+([\w.]+)\s+import|import\s+([\w., ]+))",
        flags=re.MULTILINE,
    )

    # Package manager files
    PACKAGE_FILES = [
        "requirements.txt",
        "requirements.in",
        "setup.py",
        "pyproject.toml",
        "Pipfile",
        "poetry.lock",
        "setup.cfg",
    ]

    # Standard library modules
    STDLIB = getattr(
        sys, "stdlib_module_names", []
    )  # use this below to categorise packages

    @staticmethod
    def extract_imports(code: str) -> Set[str]:
        """Extract Python imports from code."""
        imports = set()

        for match in PythonExtractor.IMPORT_PATTERN.finditer(code):
            if match.group(1):  # from X import
                module = match.group(1).split(".")[0]
                imports.add(module)
            elif match.group(2):  # import X
                modules = match.group(2).split(",")
                for module in modules:
                    module = module.strip().split(".")[0].split(" as ")[0]
                    imports.add(module)

        return imports

    @staticmethod
    def parse_requirements_txt(content: str) -> Dict[str, Optional[str]]:
        """Parse requirements.txt file and extract packages with versions."""
        packages = {}

        for line in content.split("\n"):
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Skip URLs and git repos
            if line.startswith(("http://", "https://", "git+", "-e")):
                continue

            # Extract package name and version
            # Handle operators: ==, >=, <=, >, <, ~=, !=
            match = re.match(r"^([a-zA-Z0-9_-]+)(.*)$", line)
            if match:
                pkg_name = match.group(1)
                version_spec = match.group(2).strip() if match.group(2) else None
                packages[pkg_name.lower()] = version_spec

        return packages

    @staticmethod
    def is_stdlib(module: str) -> bool:
        """Check if a module is part of the Python standard library."""
        return module in PythonExtractor.STDLIB

    @staticmethod
    def extract_install_commands(text: str) -> List[Tuple[str, str, List[str]]]:
        """
        Extract Python installation commands from PR body or commit messages.

        Returns:
            List of tuples: (package_manager, command, [packages])
            Example: [("pip", "install", ["numpy", "pandas"])]
        """
        installations = []

        # Python: pip install, pip3 install, python -m pip install
        pip_pattern = re.compile(
            r"(?:pip|pip3|python3?\s+-m\s+pip)\s+install\s+([^\n]+)",
            re.IGNORECASE,
        )
        for match in pip_pattern.finditer(text):
            packages_str = match.group(1)
            # Remove common flags (single dash followed by single letter)
            packages_str = re.sub(r"\s-[a-zA-Z]\s+\S+", " ", packages_str)
            packages_str = re.sub(r"\s-[a-zA-Z](?:\s|$)", " ", packages_str)
            # Remove long flags (double dash)
            # Only handle --flag and --flag=value, not --flag value (ambiguous with package names)
            packages_str = re.sub(
                r"\s--[a-z][a-z0-9-]*(?:=\S+)?(?:\s|$)",
                " ",
                packages_str,
            )
            # Split and clean
            packages = [
                p.strip()
                for p in packages_str.split()
                if p.strip() and not p.startswith("-") and p != "."
            ]
            if packages:
                installations.append(("pip", "install", packages))

        return installations

    @classmethod
    def extract_from_file(
        cls,
        filename: str,
        content: str,
    ) -> Tuple[Optional[Literal["code", "dependency"]], Dict[str, Optional[str]]]:
        """
        Extract libraries from a Python file based on its type.

        Returns:
            Tuple of (file_type, libraries) where file_type is "code", "dependency", or None.
        """
        filename_lower = filename.lower()

        # Check for package manager files
        if "requirements" in filename_lower and filename_lower.endswith(".txt"):
            return (
                "dependency",
                cls.parse_requirements_txt(
                    content=content,
                ),
            )
        elif filename_lower in ["setup.py", "pyproject.toml"]:
            # For now, extract imports from these too (no version info)
            imports = cls.extract_imports(
                code=content,
            )
            return ("code", {lib: None for lib in imports})
        # Check for Python code files
        elif filename.endswith(".py"):
            imports = cls.extract_imports(
                code=content,
            )
            return ("code", {lib: None for lib in imports})

        return (None, {})
