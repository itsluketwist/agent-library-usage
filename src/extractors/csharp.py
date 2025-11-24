"""C# library extraction logic."""

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Set, Tuple

from .base import BaseExtractor


class CSharpExtractor(BaseExtractor):
    """Extract libraries from C# code and dependency files."""

    # C# using statement pattern
    USING_PATTERN = re.compile(r"^\s*using\s+([\w.]+)\s*;", re.MULTILINE)

    # Package manager files
    PACKAGE_FILES = [
        "*.csproj",
        "packages.config",
        "paket.dependencies",
        "Directory.Build.props",
        "Directory.Packages.props",
    ]

    # .NET Standard library namespaces (common ones)
    STDLIB = {
        "System",
        "Microsoft.CSharp",
        "Microsoft.VisualBasic",
        "System.Collections",
        "System.ComponentModel",
        "System.Configuration",
        "System.Data",
        "System.Diagnostics",
        "System.Drawing",
        "System.Globalization",
        "System.IO",
        "System.Linq",
        "System.Net",
        "System.Reflection",
        "System.Resources",
        "System.Runtime",
        "System.Security",
        "System.Text",
        "System.Threading",
        "System.Timers",
        "System.Web",
        "System.Xml",
    }

    @staticmethod
    def extract_imports(code: str) -> Set[str]:
        """Extract C# using statements from code."""
        imports = set()

        for match in CSharpExtractor.USING_PATTERN.finditer(code):
            namespace = match.group(1)
            # Get the base namespace (first part before .)
            base_namespace = namespace.split(".")[0]
            imports.add(base_namespace)

        return imports

    @staticmethod
    def parse_csproj(content: str) -> Dict[str, Optional[str]]:
        """Parse .csproj file and extract PackageReference entries."""
        packages = {}

        try:
            # Parse XML
            root = ET.fromstring(content)

            # Find all PackageReference elements
            # Handle both old and new csproj formats
            for package_ref in root.findall(".//PackageReference"):
                # Get package name from Include attribute
                package_name = package_ref.get("Include")
                if not package_name:
                    continue

                # Get version from Version attribute or child element
                version = package_ref.get("Version")
                if not version:
                    version_elem = package_ref.find("Version")
                    if version_elem is not None and version_elem.text:
                        version = version_elem.text

                packages[package_name] = version

        except ET.ParseError:
            # If XML parsing fails, try regex fallback
            pattern = re.compile(
                r'<PackageReference\s+Include="([^"]+)"(?:\s+Version="([^"]+)")?'
            )
            for match in pattern.finditer(content):
                package_name = match.group(1)
                version = match.group(2)
                packages[package_name] = version

        return packages

    @staticmethod
    def parse_packages_config(content: str) -> Dict[str, Optional[str]]:
        """Parse packages.config file and extract package entries."""
        packages = {}

        try:
            root = ET.fromstring(content)

            # Find all package elements
            for package in root.findall(".//package"):
                package_id = package.get("id")
                version = package.get("version")

                if package_id:
                    packages[package_id] = version

        except ET.ParseError:
            # Regex fallback
            pattern = re.compile(r'<package\s+id="([^"]+)"(?:\s+version="([^"]+)")?')
            for match in pattern.finditer(content):
                package_id = match.group(1)
                version = match.group(2)
                packages[package_id] = version

        return packages

    @staticmethod
    def parse_paket_dependencies(content: str) -> Dict[str, Optional[str]]:
        """Parse paket.dependencies file."""
        packages = {}

        for line in content.split("\n"):
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("//") or line.startswith("#"):
                continue

            # Match: nuget PackageName version
            match = re.match(r"nuget\s+(\S+)(?:\s+(.+))?", line, re.IGNORECASE)
            if match:
                package_name = match.group(1)
                version = match.group(2).strip() if match.group(2) else None
                packages[package_name] = version

        return packages

    @staticmethod
    def is_stdlib(module: str) -> bool:
        """Check if a module is part of the .NET standard library."""
        return module in CSharpExtractor.STDLIB or module.startswith(
            ("System", "Microsoft")
        )

    @staticmethod
    def extract_install_commands(text: str) -> List[Tuple[str, str, List[str]]]:
        """
        Extract C#/.NET installation commands from PR body or commit messages.

        Currently C# dependencies are typically managed through .csproj or NuGet,
        so this returns an empty list. This method exists for consistency.

        Returns:
            List of tuples: (package_manager, command, [packages])
        """
        return []

    @classmethod
    def extract_from_file(cls, filename: str, content: str) -> Dict[str, Optional[str]]:
        """
        Extract libraries from a C# file based on its type.

        Returns:
            Dictionary mapping library names to their version specifications.
        """
        filename_lower = filename.lower()

        # Check for package manager files
        if filename_lower.endswith(".csproj"):
            return cls.parse_csproj(
                content=content,
            )
        elif filename_lower == "packages.config":
            return cls.parse_packages_config(
                content=content,
            )
        # Check for C# code files
        elif filename.endswith(".cs"):
            imports = cls.extract_imports(
                code=content,
            )
            return {lib: None for lib in imports}

        return {}
