"""JavaScript and TypeScript library extraction logic."""

import json
import re
from typing import Literal

from .base import BaseExtractor


class JavaScriptExtractor(BaseExtractor):
    """Extract libraries from JavaScript/TypeScript code and dependency files."""

    # JavaScript/TypeScript import pattern
    IMPORT_PATTERN = re.compile(
        r'(?:import\s+(?:.*?\s+from\s+)?["\']([^"\']+)["\']|'
        r'require\(["\']([^"\']+)["\']\))',
        re.MULTILINE,
    )

    # Package manager files
    PACKAGE_FILES = [
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
    ]

    # Node.js standard library modules
    STDLIB = {
        "fs",
        "path",
        "http",
        "https",
        "url",
        "querystring",
        "assert",
        "buffer",
        "child_process",
        "cluster",
        "crypto",
        "dns",
        "domain",
        "events",
        "net",
        "os",
        "process",
        "stream",
        "string_decoder",
        "timers",
        "tls",
        "tty",
        "dgram",
        "util",
        "v8",
        "vm",
        "zlib",
        "readline",
        "repl",
        "console",
        "module",
        "worker_threads",
    }

    @staticmethod
    def extract_imports(code: str) -> set[str]:
        """Extract JavaScript/TypeScript imports from code."""
        imports = set()

        for match in JavaScriptExtractor.IMPORT_PATTERN.finditer(code):
            module = match.group(1) or match.group(2)
            if module:
                # Remove relative imports (starting with . or /)
                if not module.startswith(".") and not module.startswith("/"):
                    # Skip path aliases (e.g., @/components, @/lib)
                    if module.startswith("@/"):
                        continue
                    # Get the package name (first part before /)
                    pkg_name = module.split("/")[0]
                    # Handle scoped packages (@scope/package)
                    if pkg_name.startswith("@") and "/" in module:
                        pkg_name = "/".join(module.split("/")[:2])
                    imports.add(pkg_name)

        return imports

    @staticmethod
    def parse_package_json(content: str) -> dict[str, str | None]:
        """Parse package.json and extract dependencies."""
        try:
            data = json.loads(content)
            packages: dict[str, str | None] = {}

            # Combine dependencies and devDependencies
            for dep_type in ["dependencies", "devDependencies", "peerDependencies"]:
                if dep_type in data:
                    packages.update(data[dep_type])

            return packages
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def is_stdlib(module: str) -> bool:
        """Check if a module is part of the Node.js standard library."""
        # Also check for node: prefix (e.g., node:path, node:fs)
        module_clean = module.replace("node:", "")
        return module_clean in JavaScriptExtractor.STDLIB

    @staticmethod
    def extract_install_commands(text: str) -> list[tuple[str, str, list[str]]]:
        """
        Extract JavaScript/Node.js installation commands from PR body or commit messages.

        Returns:
            List of tuples: (package_manager, command, [packages])
            Example: [("npm", "install", ["react", "lodash"])]
        """
        installations = []

        # Node.js: npm install, yarn add, pnpm add
        npm_pattern = re.compile(
            r"(npm|yarn|pnpm)\s+(install|add|i)\s+([^\n]+)",
            re.IGNORECASE,
        )
        for match in npm_pattern.finditer(text):
            pkg_manager = match.group(1).lower()
            packages_str = match.group(3)
            # Remove flags (single dash followed by single letter)
            packages_str = re.sub(r"\s-[a-zA-Z]\s+\S+", " ", packages_str)
            packages_str = re.sub(r"\s-[a-zA-Z](?:\s|$)", " ", packages_str)
            # Remove long flags (double dash)
            packages_str = re.sub(
                r"\s--[a-z-]+(?:=\S+)?(?:\s|$)",
                " ",
                packages_str,
            )
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

        return installations

    @classmethod
    def extract_from_file(
        cls,
        filename: str,
        content: str,
    ) -> tuple[Literal["code", "dependency"] | None, dict[str, str | None]]:
        """
        Extract libraries from a JavaScript/TypeScript file based on its type.

        Returns:
            Tuple of (file_type, libraries) where file_type is "code", "dependency", or None.
        """
        filename_lower = filename.lower()

        # Check for package manager files
        if filename_lower == "package.json":
            return (
                "dependency",
                cls.parse_package_json(
                    content=content,
                ),
            )
        # Check for JavaScript/TypeScript code files
        elif filename.endswith((".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx")):
            imports = cls.extract_imports(
                code=content,
            )
            return ("code", {lib: None for lib in imports})

        return (None, {})


class TypeScriptExtractor(JavaScriptExtractor):
    """Extract libraries from TypeScript code and dependency files.

    TypeScript uses the same import syntax as modern JavaScript,
    so we inherit from JavaScriptExtractor.
    """

    pass
