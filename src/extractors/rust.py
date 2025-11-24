"""Rust library extraction logic."""

import re
from typing import Dict, List, Literal, Optional, Set, Tuple

from .base import BaseExtractor


class RustExtractor(BaseExtractor):
    """Extract libraries from Rust code and dependency files."""

    # Rust use statement pattern
    USE_PATTERN = re.compile(
        r"^\s*(?:pub\s+)?use\s+([\w:]+)(?:::\{[^}]*\})?", re.MULTILINE
    )

    # Package manager files
    PACKAGE_FILES = ["Cargo.toml", "Cargo.lock"]

    # Rust standard library crates (common ones)
    STDLIB = {
        "std",
        "core",
        "alloc",
        "proc_macro",
        "test",
    }

    @staticmethod
    def extract_imports(code: str) -> Set[str]:
        """Extract Rust use statements from code."""
        imports = set()

        for match in RustExtractor.USE_PATTERN.finditer(code):
            crate_path = match.group(1)

            # Handle crate:: prefix
            if crate_path.startswith("crate::"):
                continue  # Internal module, skip

            # Handle self:: and super:: (relative imports)
            if crate_path.startswith(("self::", "super::")):
                continue

            # Get the crate name (first part before ::)
            crate_name = crate_path.split("::")[0]

            # Skip if it's stdlib
            if crate_name not in RustExtractor.STDLIB:
                imports.add(crate_name)

        return imports

    @staticmethod
    def parse_cargo_toml(content: str) -> Dict[str, Optional[str]]:
        """Parse Cargo.toml and extract dependencies."""
        packages = {}

        # Track which section we're in
        in_dependencies = False
        in_dev_dependencies = False
        in_build_dependencies = False

        for line in content.split("\n"):
            line = line.strip()

            # Check for section headers
            if line == "[dependencies]":
                in_dependencies = True
                in_dev_dependencies = False
                in_build_dependencies = False
                continue
            elif line == "[dev-dependencies]":
                in_dependencies = False
                in_dev_dependencies = True
                in_build_dependencies = False
                continue
            elif line == "[build-dependencies]":
                in_dependencies = False
                in_dev_dependencies = False
                in_build_dependencies = True
                continue
            elif line.startswith("[") and (
                in_dependencies or in_dev_dependencies or in_build_dependencies
            ):
                # Entering a different section
                in_dependencies = False
                in_dev_dependencies = False
                in_build_dependencies = False
                continue

            # Parse dependencies (include all types)
            if (
                in_dependencies or in_dev_dependencies or in_build_dependencies
            ) and "=" in line:
                # Simple format: package = "version"
                if '"' in line or "'" in line:
                    parts = line.split("=", 1)
                    pkg_name = parts[0].strip()
                    version_part = parts[1].strip().strip("\"'")

                    # Handle version only (not table format)
                    if not version_part.startswith("{"):
                        packages[pkg_name] = version_part
                    else:
                        # Table format: package = { version = "..." }
                        version_match = re.search(
                            r'version\s*=\s*["\']([^"\']+)["\']', version_part
                        )
                        if version_match:
                            packages[pkg_name] = version_match.group(1)
                        else:
                            packages[pkg_name] = None
                # Table format on separate lines
                elif in_dependencies or in_dev_dependencies or in_build_dependencies:
                    # package.version = "..."
                    match = re.match(r'(\w+)\.version\s*=\s*["\']([^"\']+)["\']', line)
                    if match:
                        pkg_name = match.group(1)
                        version = match.group(2)
                        packages[pkg_name] = version

        return packages

    @staticmethod
    def is_stdlib(module: str) -> bool:
        """Check if a module is part of the Rust standard library."""
        return module in RustExtractor.STDLIB

    @staticmethod
    def extract_install_commands(text: str) -> List[Tuple[str, str, List[str]]]:
        """
        Extract Rust installation commands from PR body or commit messages.

        Currently Rust dependencies are typically managed through Cargo.toml,
        so this returns an empty list. This method exists for consistency.

        Returns:
            List of tuples: (package_manager, command, [packages])
        """
        return []

    @classmethod
    def extract_from_file(
        cls,
        filename: str,
        content: str,
    ) -> Tuple[Optional[Literal["code", "dependency"]], Dict[str, Optional[str]]]:
        """
        Extract libraries from a Rust file based on its type.

        Returns:
            Tuple of (file_type, libraries) where file_type is "code", "dependency", or None.
        """
        filename_lower = filename.lower()

        # Check for package manager files
        if filename_lower == "cargo.toml":
            return (
                "dependency",
                cls.parse_cargo_toml(
                    content=content,
                ),
            )
        # Check for Rust code files
        elif filename.endswith(".rs"):
            imports = cls.extract_imports(
                code=content,
            )
            return ("code", {lib: None for lib in imports})

        return (None, {})
