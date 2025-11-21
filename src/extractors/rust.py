"""Rust library extraction logic."""

from typing import Dict


class RustExtractor:
    """Extract libraries from Rust code and dependency files."""

    # Package manager files
    PACKAGE_FILES = ["Cargo.toml", "Cargo.lock"]

    @staticmethod
    def parse_cargo_toml(content: str) -> Dict[str, str]:
        """Parse Cargo.toml and extract dependencies."""
        packages = {}

        in_dependencies = False
        for line in content.split("\n"):
            line = line.strip()

            if line == "[dependencies]":
                in_dependencies = True
                continue
            elif line.startswith("[") and in_dependencies:
                in_dependencies = False
                continue

            if in_dependencies and "=" in line:
                parts = line.split("=", 1)
                pkg_name = parts[0].strip()
                version = parts[1].strip().strip("\"'")
                packages[pkg_name] = version

        return packages
