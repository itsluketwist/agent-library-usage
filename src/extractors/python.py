"""Python library extraction logic."""

import re
import sys
import tomllib
from typing import Literal

from .base import BaseExtractor


class PythonExtractor(BaseExtractor):
    """Extract libraries from Python code and dependency files."""

    # Python import pattern
    IMPORT_PATTERN = re.compile(
        pattern=r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w., ]+))",
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
    def extract_imports(code: str) -> set[str]:
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
    def parse_requirements_txt(content: str) -> dict[str, str | None]:
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
    def parse_pyproject_toml(content: str) -> dict[str, str | None]:
        """Parse pyproject.toml file and extract dependencies."""
        packages: dict[str, str | None] = {}

        try:
            data = tomllib.loads(content)

            # PEP 621 style: [project.dependencies]
            if "project" in data and "dependencies" in data["project"]:
                for dep in data["project"]["dependencies"]:
                    # Dependencies are in format: "package>=1.0.0" or "package"
                    match = re.match(r"^([a-zA-Z0-9_-]+)(.*)$", dep.strip())
                    if match:
                        pkg_name = match.group(1)
                        version_spec = (
                            match.group(2).strip() if match.group(2) else None
                        )
                        packages[pkg_name.lower()] = version_spec

            # Poetry style: [tool.poetry.dependencies]
            if "tool" in data and "poetry" in data["tool"]:
                poetry_deps = data["tool"]["poetry"].get("dependencies", {})
                for pkg_name, version_spec in poetry_deps.items():
                    # Skip python version constraint
                    if pkg_name.lower() == "python":
                        continue

                    # Version can be a string or a dict
                    if isinstance(version_spec, str):
                        packages[pkg_name.lower()] = version_spec
                    elif isinstance(version_spec, dict):
                        # Handle dict format: {version = "^1.0", extras = [...]}
                        version = version_spec.get("version")
                        packages[pkg_name.lower()] = version
                    else:
                        packages[pkg_name.lower()] = None

                # Also check dev-dependencies
                poetry_dev_deps = data["tool"]["poetry"].get("dev-dependencies", {})
                for pkg_name, version_spec in poetry_dev_deps.items():
                    if isinstance(version_spec, str):
                        packages[pkg_name.lower()] = version_spec
                    elif isinstance(version_spec, dict):
                        version = version_spec.get("version")
                        packages[pkg_name.lower()] = version
                    else:
                        packages[pkg_name.lower()] = None

        except (tomllib.TOMLDecodeError, KeyError, AttributeError):
            # If parsing fails, return empty dict
            pass

        return packages

    @staticmethod
    def is_stdlib(module: str) -> bool:
        """Check if a module is part of the Python standard library."""
        return module in PythonExtractor.STDLIB

    @staticmethod
    def extract_install_commands(text: str) -> list[tuple[str, str, list[str]]]:
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
    ) -> tuple[Literal["code", "dependency"] | None, dict[str, str | None]]:
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
        elif filename_lower == "pyproject.toml":
            return (
                "dependency",
                cls.parse_pyproject_toml(
                    content=content,
                ),
            )
        elif filename_lower == "setup.py":
            # For setup.py, extract imports from code (no version info)
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
