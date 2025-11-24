"""Main library extractor facade that routes to language-specific extractors."""

from typing import Dict, Optional, Set

from .base import BaseExtractor
from .csharp import CSharpExtractor
from .go import GoExtractor
from .javascript import JavaScriptExtractor, TypeScriptExtractor
from .python import PythonExtractor
from .rust import RustExtractor


class LibraryExtractor(BaseExtractor):
    """Main facade for extracting libraries from code files across different languages."""

    # Package manager file patterns (aggregated from all extractors)
    PACKAGE_FILES = {
        "python": PythonExtractor.PACKAGE_FILES,
        "javascript": JavaScriptExtractor.PACKAGE_FILES,
        "typescript": JavaScriptExtractor.PACKAGE_FILES,
        "go": GoExtractor.PACKAGE_FILES,
        "rust": RustExtractor.PACKAGE_FILES,
        "csharp": CSharpExtractor.PACKAGE_FILES,
        "ruby": ["Gemfile", "Gemfile.lock", ".gemspec"],
        "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
        "php": ["composer.json", "composer.lock"],
    }

    @staticmethod
    def extract_python_imports(code: str) -> Set[str]:
        """Extract Python imports from code."""
        return PythonExtractor.extract_imports(code)

    @staticmethod
    def extract_js_imports(code: str) -> Set[str]:
        """Extract JavaScript/Node.js imports from code."""
        return JavaScriptExtractor.extract_imports(code)

    @staticmethod
    def extract_typescript_imports(code: str) -> Set[str]:
        """Extract TypeScript imports from code."""
        return TypeScriptExtractor.extract_imports(code)

    @staticmethod
    def extract_go_imports(code: str) -> Set[str]:
        """Extract Go imports from code."""
        return GoExtractor.extract_imports(code)

    @staticmethod
    def extract_rust_imports(code: str) -> Set[str]:
        """Extract Rust use statements from code."""
        return RustExtractor.extract_imports(code)

    @staticmethod
    def extract_csharp_imports(code: str) -> Set[str]:
        """Extract C# using statements from code."""
        return CSharpExtractor.extract_imports(code)

    @staticmethod
    def parse_requirements_txt(content: str) -> Dict[str, Optional[str]]:
        """Parse requirements.txt file and extract packages with versions."""
        return PythonExtractor.parse_requirements_txt(content)

    @staticmethod
    def parse_package_json(content: str) -> Dict[str, str]:
        """Parse package.json and extract dependencies."""
        return JavaScriptExtractor.parse_package_json(content)

    @staticmethod
    def parse_go_mod(content: str) -> Dict[str, str]:
        """Parse go.mod file and extract dependencies."""
        return GoExtractor.parse_go_mod(content)

    @staticmethod
    def parse_cargo_toml(content: str) -> Dict[str, Optional[str]]:
        """Parse Cargo.toml and extract dependencies."""
        return RustExtractor.parse_cargo_toml(content)

    @staticmethod
    def parse_csproj(content: str) -> Dict[str, Optional[str]]:
        """Parse .csproj file and extract PackageReference entries."""
        return CSharpExtractor.parse_csproj(content)

    @staticmethod
    def parse_packages_config(content: str) -> Dict[str, Optional[str]]:
        """Parse packages.config file and extract package entries."""
        return CSharpExtractor.parse_packages_config(content)

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

        elif language.lower() == "csharp":
            if filename_lower.endswith(".csproj"):
                return set(cls.parse_csproj(content).keys())
            elif filename_lower == "packages.config":
                return set(cls.parse_packages_config(content).keys())

        # Extract from code files based on extension
        if filename.endswith(".py"):
            return cls.extract_python_imports(content)
        elif filename.endswith((".js", ".jsx", ".mjs", ".cjs")):
            return cls.extract_js_imports(content)
        elif filename.endswith((".ts", ".tsx")):
            return cls.extract_typescript_imports(content)
        elif filename.endswith(".go"):
            return cls.extract_go_imports(content)
        elif filename.endswith(".rs"):
            return cls.extract_rust_imports(content)
        elif filename.endswith(".cs"):
            return cls.extract_csharp_imports(content)

        return set()

    @staticmethod
    def is_stdlib(module: str, language: str) -> bool:
        """Check if a module is part of the standard library."""
        if language.lower() == "python":
            return PythonExtractor.is_stdlib(module)
        elif language.lower() in ["javascript", "typescript"]:
            return JavaScriptExtractor.is_stdlib(module)
        elif language.lower() == "go":
            return GoExtractor.is_stdlib(module)
        elif language.lower() == "rust":
            return RustExtractor.is_stdlib(module)
        elif language.lower() == "csharp":
            return CSharpExtractor.is_stdlib(module)

        return False
