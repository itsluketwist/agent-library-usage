"""Go library extraction logic."""

import re
from typing import Dict, List, Literal, Optional, Set, Tuple

from .base import BaseExtractor


class GoExtractor(BaseExtractor):
    """Extract libraries from Go code and dependency files."""

    # Go import pattern
    IMPORT_PATTERN = re.compile(
        r'^\s*(?:_\s+|[a-zA-Z0-9_]+\s+|\.\s+)?import\s+(?:"([^"]+)"|(\([\s\S]*?\)))',
        re.MULTILINE,
    )

    # Package manager files
    PACKAGE_FILES = ["go.mod", "go.sum"]

    # Go standard library packages (common ones)
    STDLIB = {
        "fmt",
        "os",
        "io",
        "bufio",
        "bytes",
        "strings",
        "strconv",
        "errors",
        "log",
        "math",
        "time",
        "sort",
        "sync",
        "context",
        "encoding/json",
        "encoding/xml",
        "encoding/csv",
        "encoding/base64",
        "net",
        "net/http",
        "net/url",
        "path",
        "path/filepath",
        "regexp",
        "runtime",
        "testing",
        "flag",
        "reflect",
        "unsafe",
        "container/list",
        "container/heap",
        "database/sql",
        "text/template",
        "html/template",
        "crypto",
        "crypto/md5",
        "crypto/sha1",
        "crypto/sha256",
        "os/exec",
    }

    @staticmethod
    def extract_imports(code: str) -> Set[str]:
        """Extract Go imports from code."""
        imports = set()

        for match in GoExtractor.IMPORT_PATTERN.finditer(code):
            if match.group(1):
                # Single import: import "package"
                pkg = match.group(1)
                # Extract the base package (first part of path)
                # e.g., "github.com/user/repo/pkg" -> "github.com/user/repo"
                parts = pkg.split("/")
                if len(parts) >= 3:
                    # For paths like github.com/user/repo
                    imports.add("/".join(parts[:3]))
                else:
                    # Standard library or short import
                    imports.add(pkg)
            elif match.group(2):
                # Multiple imports: import ( ... )
                import_block = match.group(2)
                # Extract all quoted strings
                for line in import_block.split("\n"):
                    line = line.strip()
                    # Handle aliased imports: _ "pkg", alias "pkg", . "pkg"
                    alias_match = re.match(r'^(?:_|[a-zA-Z0-9_]+|\.)\s+"([^"]+)"', line)
                    if alias_match:
                        pkg = alias_match.group(1)
                    elif line.startswith('"') and line.endswith('"'):
                        pkg = line.strip('"')
                    else:
                        continue

                    parts = pkg.split("/")
                    if len(parts) >= 3:
                        imports.add("/".join(parts[:3]))
                    else:
                        imports.add(pkg)

        return imports

    @staticmethod
    def parse_go_mod(content: str) -> Dict[str, str]:
        """Parse go.mod file and extract dependencies."""
        packages = {}

        in_require_block = False
        for line in content.split("\n"):
            line = line.strip()

            if line.startswith("require ("):
                in_require_block = True
                continue
            elif line == ")" and in_require_block:
                in_require_block = False
                continue

            if in_require_block or line.startswith("require "):
                # Extract module and version
                parts = line.replace("require ", "").strip().split()
                if len(parts) >= 2:
                    packages[parts[0]] = parts[1]

        return packages

    @staticmethod
    def is_stdlib(module: str) -> bool:
        """Check if a module is part of the Go standard library."""
        # Stdlib packages don't have / in them (generally)
        # or they're in the known stdlib list
        return module in GoExtractor.STDLIB or "/" not in module

    @staticmethod
    def extract_install_commands(text: str) -> List[Tuple[str, str, List[str]]]:
        """
        Extract Go installation commands from PR body or commit messages.

        Returns:
            List of tuples: (package_manager, command, [packages])
            Example: [("go", "get", ["github.com/user/repo"])]
        """
        installations = []

        # Go: go get, go install
        go_pattern = re.compile(
            r"go\s+(get|install)\s+([^\n]+)",
            re.IGNORECASE,
        )
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

    @classmethod
    def extract_from_file(
        cls,
        filename: str,
        content: str,
    ) -> Tuple[Optional[Literal["code", "dependency"]], Dict[str, Optional[str]]]:
        """
        Extract libraries from a Go file based on its type.

        Returns:
            Tuple of (file_type, libraries) where file_type is "code", "dependency", or None.
        """
        filename_lower = filename.lower()

        # Check for package manager files
        if filename_lower == "go.mod":
            return (
                "dependency",
                cls.parse_go_mod(
                    content=content,
                ),
            )
        # Check for Go code files
        elif filename.endswith(".go"):
            imports = cls.extract_imports(
                code=content,
            )
            return ("code", {lib: None for lib in imports})

        return (None, {})
