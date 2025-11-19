"""Extract library/dependency information from code files and PRs."""

import json
import re
from typing import Dict, List, Optional, Set, Tuple


class LibraryExtractor:
    """Extract libraries from code files across different languages."""

    # Language-specific import patterns
    PYTHON_IMPORT_PATTERN = re.compile(
        r"^(?:from\s+([\w.]+)\s+import|import\s+([\w., ]+))", re.MULTILINE
    )

    JS_IMPORT_PATTERN = re.compile(
        r'(?:import\s+(?:.*?\s+from\s+)?["\']([^"\']+)["\']|'
        r'require\(["\']([^"\']+)["\']\))',
        re.MULTILINE,
    )

    TYPESCRIPT_IMPORT_PATTERN = re.compile(
        r'import\s+.*?\s+from\s+["\']([^"\']+)["\']', re.MULTILINE
    )

    GO_IMPORT_PATTERN = re.compile(
        r'^\s*(?:_\s+|[a-zA-Z0-9_]+\s+|\.\s+)?import\s+(?:"([^"]+)"|(\([\s\S]*?\)))',
        re.MULTILINE,
    )

    # Package manager file patterns
    PACKAGE_FILES = {
        "python": [
            "requirements.txt",
            "requirements.in",
            "setup.py",
            "pyproject.toml",
            "Pipfile",
            "poetry.lock",
            "setup.cfg",
        ],
        "javascript": [
            "package.json",
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
        ],
        "typescript": [
            "package.json",
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
        ],
        "ruby": ["Gemfile", "Gemfile.lock", ".gemspec"],
        "go": ["go.mod", "go.sum"],
        "rust": ["Cargo.toml", "Cargo.lock"],
        "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
        "php": ["composer.json", "composer.lock"],
        "csharp": ["*.csproj", "packages.config", "paket.dependencies"],
    }

    # Version specification patterns
    VERSION_PATTERN = re.compile(r"([=<>!~]+)?\s*(\d+(?:\.\d+)*(?:\.\*)?)")

    @staticmethod
    def extract_python_imports(code: str) -> Set[str]:
        """Extract Python imports from code."""
        imports = set()

        for match in LibraryExtractor.PYTHON_IMPORT_PATTERN.finditer(code):
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
    def extract_js_imports(code: str) -> Set[str]:
        """Extract JavaScript/Node.js imports from code."""
        imports = set()

        for match in LibraryExtractor.JS_IMPORT_PATTERN.finditer(code):
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
    def extract_typescript_imports(code: str) -> Set[str]:
        """Extract TypeScript imports from code."""
        # TypeScript uses same import syntax as modern JavaScript
        return LibraryExtractor.extract_js_imports(code)

    @staticmethod
    def extract_go_imports(code: str) -> Set[str]:
        """Extract Go imports from code."""
        imports = set()

        for match in LibraryExtractor.GO_IMPORT_PATTERN.finditer(code):
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

    @staticmethod
    def has_version_spec(version_str: Optional[str]) -> bool:
        """Check if a version string contains a version specification."""
        if not version_str:
            return False
        return bool(LibraryExtractor.VERSION_PATTERN.search(version_str))

    @staticmethod
    def extract_version_operator(version_str: str) -> Optional[str]:
        """Extract the version operator (e.g., ==, >=, ~, ^) from version string."""
        operators = ["==", ">=", "<=", ">", "<", "~=", "!=", "^", "~"]
        for op in operators:
            if op in version_str:
                return op
        return None

    @classmethod
    def extract_from_file(cls, filename: str, content: str, language: str) -> Set[str]:
        """Extract libraries from a file based on its type and language."""
        filename_lower = filename.lower()

        # Check if it's a package manager file
        if language.lower() == "python":
            if "requirements" in filename_lower and filename_lower.endswith(".txt"):
                return set(cls.parse_requirements_txt(content).keys())
            elif filename_lower in ["setup.py", "pyproject.toml"]:
                # For now, extract imports from these too
                return cls.extract_python_imports(content)

        elif language.lower() in ["javascript", "typescript"]:
            if filename_lower == "package.json":
                return set(cls.parse_package_json(content).keys())

        elif language.lower() == "go":
            if filename_lower == "go.mod":
                return set(cls.parse_go_mod(content).keys())

        elif language.lower() == "rust":
            if filename_lower == "cargo.toml":
                return set(cls.parse_cargo_toml(content).keys())

        # Extract from code files based on extension
        if filename.endswith(".py"):
            return cls.extract_python_imports(content)
        elif filename.endswith((".js", ".jsx", ".mjs", ".cjs")):
            return cls.extract_js_imports(content)
        elif filename.endswith((".ts", ".tsx")):
            return cls.extract_typescript_imports(content)
        elif filename.endswith(".go"):
            return cls.extract_go_imports(content)

        return set()

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
            packages_str = re.sub(r"\s--[a-z][a-z0-9-]*(?:=\S+)?(?:\s|$)", " ", packages_str)
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

    @staticmethod
    def is_stdlib(module: str, language: str) -> bool:
        """Check if a module is part of the standard library."""
        # Common Python stdlib modules
        python_stdlib = {
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
        }

        # Common Node.js stdlib modules
        node_stdlib = {
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

        # Common Go stdlib packages
        go_stdlib = {
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
        }

        if language.lower() == "python":
            return module in python_stdlib
        elif language.lower() in ["javascript", "typescript"]:
            return module in node_stdlib
        elif language.lower() == "go":
            return module in go_stdlib or "/" not in module  # stdlib doesn't have /

        return False
