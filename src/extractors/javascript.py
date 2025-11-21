"""JavaScript and TypeScript library extraction logic."""

import json
import re
from typing import Dict, Set


class JavaScriptExtractor:
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
    def extract_imports(code: str) -> Set[str]:
        """Extract JavaScript/TypeScript imports from code."""
        imports = set()

        for match in JavaScriptExtractor.IMPORT_PATTERN.finditer(code):
            module = match.group(1) or match.group(2)
            if module:
                # Remove relative imports (starting with . or /)
                if not module.startswith(".") and not module.startswith("/"):
                    # Get the package name (first part before /)
                    pkg_name = module.split("/")[0]
                    # Handle scoped packages (@scope/package)
                    if pkg_name.startswith("@") and "/" in module:
                        pkg_name = "/".join(module.split("/")[:2])
                    imports.add(pkg_name)

        return imports

    @staticmethod
    def parse_package_json(content: str) -> Dict[str, str]:
        """Parse package.json and extract dependencies."""
        try:
            data = json.loads(content)
            packages = {}

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


class TypeScriptExtractor(JavaScriptExtractor):
    """Extract libraries from TypeScript code and dependency files.

    TypeScript uses the same import syntax as modern JavaScript,
    so we inherit from JavaScriptExtractor.
    """

    pass
