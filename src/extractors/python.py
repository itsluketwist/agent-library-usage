"""Python library extraction logic."""

import re
from typing import Dict, Optional, Set


class PythonExtractor:
    """Extract libraries from Python code and dependency files."""

    # Python import pattern
    IMPORT_PATTERN = re.compile(
        r"^(?:from\s+([\w.]+)\s+import|import\s+([\w., ]+))", re.MULTILINE
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
    STDLIB = {
        "os",
        "sys",
        "math",
        "json",
        "re",
        "datetime",
        "time",
        "random",
        "collections",
        "itertools",
        "functools",
        "pathlib",
        "typing",
        "unittest",
        "logging",
        "argparse",
        "subprocess",
        "threading",
        "multiprocessing",
        "queue",
        "socket",
        "urllib",
        "http",
        "email",
        "io",
        "csv",
        "xml",
        "html",
        "string",
        "copy",
        "pickle",
        "shelve",
        "sqlite3",
        "enum",
        "dataclasses",
        "abc",
        "contextlib",
        "warnings",
        "tempfile",
        "shutil",
        "glob",
        "fnmatch",
        "hashlib",
        "base64",
        "uuid",
        "secrets",
        "platform",
        "traceback",
        "inspect",
        "ast",
        "__future__",
        "asyncio",
    }

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
