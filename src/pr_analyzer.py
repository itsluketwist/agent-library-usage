"""Analyse pull requests for library usage patterns."""

from collections import Counter
from dataclasses import dataclass

import pandas as pd

from .extractors import get_extractor


# Known self-import packages that slip through our filters
# These are project-specific packages that appear in PRs but shouldn't count as external libraries
KNOWN_SELF_IMPORTS = {
    "python": {
        "alpha_factory_v1",
        "meta_agent",
        "src",
        "app",
        "backend",
        "frontend",
    },
    "rust": {
        "glaredb_error",
        "near_primitives",
        "near_primitives_core",
        "near_async",
        "near_epoch_manager",
        "near_chain_configs",
        "near_chain",
        "near_vm_runner",
        "near_crypto",
        "near_o11y",
        "near_network",
        "web_pages",
        "daisy_rsx",
        "db",
        "core",
        "common",
    },
    "typescript": {
        "@calcom/lib",
        "@calcom/prisma",
        "@calcom/features",
        "@calcom/ui",
        "src",
    },
    "go": {
        "github.com/tphakala/birdnet-go",
        "code.vikunja.io/api",
        "code.vikunja.io/api/pkg",  # Sometimes extracted with /pkg suffix
    },
    "csharp": {
        "StaticViewLocator",
        "Analyzer",
        "UITest",
        "AzureMcp",
        "TestFramework",
    },
}


@dataclass
class LibraryUsage:
    """Statistics about library usage in a PR."""

    pr_id: int
    repo_id: int
    language: str
    agent: str

    # used imports found
    stdlib_imports: set[str]
    extlib_imports: set[str]

    # new dependencies found
    dep_no_version: set[str]
    dep_with_version: set[str]

    def to_dict(self) -> dict:
        """Convert to dictionary for serialisation."""
        return {
            "pr_id": self.pr_id,
            "repo_id": self.repo_id,
            "language": self.language,
            "agent": self.agent,
            "stdlib_imports": list(self.stdlib_imports),
            "extlib_imports": list(self.extlib_imports),
            "dep_no_version": list(self.dep_no_version),
            "dep_with_version": list(self.dep_with_version),
        }


class PRAnalyzer:
    """Analyse pull requests for library usage patterns."""

    def analyse_commit_details(
        self,
        commit_details: pd.DataFrame,
        language: str,
    ) -> dict[int, LibraryUsage]:
        """
        Analyse commit details for library usage.

        Returns:
            Dictionary mapping pr_id to LibraryUsage
        """
        results = {}

        # Group by PR
        for pr_id, pr_commits in commit_details.groupby("pull_request_id"):
            usage = self._analyze_pr_commits(
                pr_id=pr_id,
                commits_df=pr_commits,
                language=language,
            )
            results[pr_id] = usage

        return results

    def _analyze_pr_commits(
        self,
        pr_id: int,
        commits_df: pd.DataFrame,
        language: str,
    ) -> LibraryUsage:
        """Analyse a single PR's commits for library usage."""

        # Get the extractor for this language
        extractor_class = get_extractor(
            language=language,
        )
        if not extractor_class:
            raise ValueError(f"Unsupported language: {language}")

        # Extract basic info
        repo_id: int = int(commits_df.iloc[0]["repo_id"])
        agent: str = commits_df.iloc[0]["agent"]

        # code import data
        stdlib_imports = set()
        extlib_imports = set()

        # dependency file data
        dep_with_version = set()
        dep_no_version = set()

        # Infer project package names from file paths
        project_packages = self._infer_project_packages(commits_df, language)

        # Process each file change
        for _, row in commits_df.iterrows():
            filename = row.get("filename", "")
            patch = row.get("patch", "")
            content = self._extract_content_from_patch(patch) if patch else ""

            if not filename or not content:
                continue

            # Extract libraries using extractor
            file_type, libs_dict = extractor_class.extract_from_file(
                filename=filename,
                content=content,
            )

            # Process the extracted libraries based on file type
            if file_type == "code":
                # Code file: categorize imports as stdlib or external
                for lib in libs_dict.keys():
                    # Skip project's own packages
                    if self._is_project_package(lib, project_packages, language):
                        continue
                    # Categorize as stdlib or external
                    if extractor_class.is_stdlib(module=lib):
                        stdlib_imports.add(lib)
                    else:
                        extlib_imports.add(lib)
            elif file_type == "dependency":
                # Dependency file: categorize by whether version is specified
                for lib, version in libs_dict.items():
                    # Skip project's own packages
                    if self._is_project_package(lib, project_packages, language):
                        continue
                    if version:
                        dep_with_version.add(lib)
                    else:
                        dep_no_version.add(lib)

        return LibraryUsage(
            pr_id=pr_id,
            repo_id=repo_id,
            language=language,
            agent=agent,
            stdlib_imports=stdlib_imports,
            extlib_imports=extlib_imports,
            dep_no_version=dep_no_version,
            dep_with_version=dep_with_version,
        )

    def _is_project_package(
        self,
        lib: str,
        project_packages: set[str],
        language: str,
    ) -> bool:
        """
        Check if a library is a project package.

        For Go, uses prefix matching (e.g., "mochi" matches "mochi/parser").
        For other languages, uses exact matching.
        Also checks against a hardcoded blocklist of known self-imports.
        """
        # Check hardcoded blocklist first
        if language in KNOWN_SELF_IMPORTS and lib in KNOWN_SELF_IMPORTS[language]:
            return True

        if language == "go":
            # For Go, check if the library starts with any project package prefix
            for pkg in project_packages:
                if lib == pkg or lib.startswith(f"{pkg}/"):
                    return True
            return False
        else:
            # For other languages, use exact matching
            return lib in project_packages

    def _infer_project_packages(
        self,
        commits_df: pd.DataFrame,
        language: str,
    ) -> set[str]:
        """
        Infer project package names from file paths in the PR.

        Language-specific heuristics:
        - Python: Top-level directories with .py files
        - Go: Package paths extracted from .go file paths
        - Rust: Top-level crate names from file paths
        - C#: Sample/test applications in specific directories
        - JavaScript/TypeScript: Already filtered in extractor via @/ pattern

        Returns:
            Set of inferred package names
        """
        project_packages = set()

        if language == "python":
            # Look for patterns like: package_name/__init__.py, package_name/submodule/file.py
            # or any directory containing files
            for filename in commits_df["filename"]:
                if not isinstance(filename, str):
                    continue

                parts = filename.split("/")
                # Check if this is in a subdirectory
                if len(parts) >= 2:
                    # The first part might be a package name
                    potential_package = parts[0]
                    # Valid Python package names contain only letters, numbers, underscores
                    if potential_package and all(
                        c.isalnum() or c == "_" for c in potential_package
                    ):
                        # Add if it's a Python file in a subdirectory
                        if filename.endswith(".py"):
                            project_packages.add(potential_package)
                        # Or if the directory name looks like a Python package (contains underscore)
                        # This catches cases like alpha_factory_v1/README.md
                        elif "_" in potential_package:
                            project_packages.add(potential_package)

        elif language == "rust":
            # Look for crate names from file paths like: crates/glaredb_error/src/lib.rs
            # or any directory containing Rust files
            for filename in commits_df["filename"]:
                if not isinstance(filename, str):
                    continue

                parts = filename.split("/")
                # Pattern: crates/CRATE_NAME/... or just CRATE_NAME/src/...
                if len(parts) >= 2:
                    if parts[0] == "crates" and len(parts) >= 3:
                        project_packages.add(parts[1])
                    elif filename.endswith(".rs") and parts[1] in (
                        "src",
                        "tests",
                        "benches",
                        "examples",
                    ):
                        # First part is likely the crate name
                        if all(c.isalnum() or c == "_" for c in parts[0]):
                            project_packages.add(parts[0])
                    elif filename.endswith(".rs"):
                        # For any Rust file in a subdirectory, the first part is likely a crate name
                        if all(c.isalnum() or c == "_" for c in parts[0]):
                            project_packages.add(parts[0])

        elif language == "go":
            # Look for Go package paths from .go files
            # Pattern: package_path/file.go -> extract base project name
            # If we see "mochi/parser/lexer.go", infer that anything starting with "mochi/" is a project package
            base_packages = set()
            for filename in commits_df["filename"]:
                if not isinstance(filename, str) or not filename.endswith(".go"):
                    continue

                parts = filename.split("/")
                if len(parts) >= 2:
                    # Get the base package (first part before any slashes)
                    # "mochi/parser/lexer.go" -> "mochi"
                    # "cmd/tool/main.go" -> "cmd"
                    base_packages.add(parts[0])

            # Now add these base packages to project_packages
            # We'll use these as prefixes when filtering
            project_packages.update(base_packages)

        elif language == "csharp":
            # Look for sample/test applications in paths
            for filename in commits_df["filename"]:
                if not isinstance(filename, str):
                    continue

                parts = filename.split("/")
                if len(parts) >= 2:
                    # Check for samples/ or tests/ directories
                    if parts[0] in ("samples", "test", "tests", "examples"):
                        # Next part is the sample/test app name
                        if all(c.isalnum() or c in (".", "_") for c in parts[1]):
                            project_packages.add(parts[1])

        # JavaScript/TypeScript already filtered in extractor

        return project_packages

    def _extract_content_from_patch(self, patch: str) -> str:
        """
        Extract added content from a unified diff patch.

        Returns:
            Content of added lines (without + prefix)
        """
        if not patch or not isinstance(patch, str):
            return ""

        lines = []
        for line in patch.split("\n"):
            # Skip diff headers
            if (
                line.startswith("@@")
                or line.startswith("+++")
                or line.startswith("---")
            ):
                continue
            # Extract added lines (start with +)
            if line.startswith("+"):
                lines.append(line[1:])  # Remove the + prefix

        return "\n".join(lines)

    @staticmethod
    def aggregate_statistics(
        usages: list[LibraryUsage],
        pr_merge_status: dict[int, bool] | None = None,
    ) -> dict[str, int | float | list[tuple[str, int]] | list[tuple[str, int, float]]]:
        """Aggregate statistics across multiple PR library usages."""

        total_prs = len(usages)
        if total_prs == 0:
            return {}

        # Count unique libraries across all PRs
        all_stdlib = set().union(*[u.stdlib_imports for u in usages])
        all_extlib = set().union(*[u.extlib_imports for u in usages])
        all_dep_with_ver = set().union(*[u.dep_with_version for u in usages])
        all_dep_no_ver = set().union(*[u.dep_no_version for u in usages])
        all_new_deps = all_dep_with_ver | all_dep_no_ver

        # RQ1: Library Usage - Count PRs with stdlib/extlib imports
        prs_with_stdlib = sum(1 for u in usages if u.stdlib_imports)
        prs_with_extlib = sum(1 for u in usages if u.extlib_imports)
        prs_with_any_import = sum(
            1 for u in usages if u.stdlib_imports or u.extlib_imports
        )

        # RQ2: New Dependencies - Count PRs with dependencies
        prs_with_deps = sum(1 for u in usages if u.dep_with_version or u.dep_no_version)
        total_new_deps = sum(
            len(u.dep_with_version) + len(u.dep_no_version) for u in usages
        )
        total_new_deps_with_ver = sum(len(u.dep_with_version) for u in usages)

        # RQ3: Choosing Libraries - Count PRs per new dependency
        new_dep_counter = Counter(
            lib for u in usages for lib in (u.dep_with_version | u.dep_no_version)
        )
        top_new_deps = [
            (lib, count, 100 * count / total_prs)
            for lib, count in new_dep_counter.most_common(20)
        ]

        # RQ3: External library imports - Count PRs per external library
        extlib_counter = Counter(lib for u in usages for lib in u.extlib_imports)
        top_extlib_imports = [
            (lib, count, 100 * count / total_prs)
            for lib, count in extlib_counter.most_common(20)
        ]

        stats = {
            # General stats
            "total_prs": total_prs,
            # RQ1: Library Usage
            "prs_with_stdlib": prs_with_stdlib,
            "pct_prs_with_stdlib": 100 * prs_with_stdlib / total_prs
            if total_prs > 0
            else 0,
            "prs_with_extlib": prs_with_extlib,
            "pct_prs_with_extlib": 100 * prs_with_extlib / total_prs
            if total_prs > 0
            else 0,
            "prs_with_any_import": prs_with_any_import,
            "pct_prs_with_any_import": 100 * prs_with_any_import / total_prs
            if total_prs > 0
            else 0,
            "avg_stdlib_per_pr": sum(len(u.stdlib_imports) for u in usages) / total_prs,
            "avg_extlib_per_pr": sum(len(u.extlib_imports) for u in usages) / total_prs,
            # RQ2: New Dependencies
            "prs_with_new_deps": prs_with_deps,
            "pct_prs_with_new_deps": 100 * prs_with_deps / total_prs
            if total_prs > 0
            else 0,
            "avg_new_deps_per_pr": total_new_deps / total_prs,
            "total_new_deps": total_new_deps,  # Total count of dependency additions
            "total_new_deps_with_version": total_new_deps_with_ver,  # Count with version
            "pct_new_deps_with_version": 100 * total_new_deps_with_ver / total_new_deps
            if total_new_deps > 0
            else 0,
            "total_unique_new_deps": len(all_new_deps),
            "pct_unique_new_deps": 100 * len(all_new_deps) / total_new_deps
            if total_new_deps > 0
            else 0,
            # RQ3: Choosing Libraries
            "top_new_deps": top_new_deps,  # List of (lib, count, pct)
            "top_extlib_imports": top_extlib_imports,  # List of (lib, count, pct)
            "total_unique_extlib_imports": len(all_extlib),
            # Legacy stats for backwards compatibility
            "total_stdlib_imports": len(all_stdlib),
            "total_extlib_imports": len(all_extlib),
            "most_common_stdlib": Counter(
                lib for u in usages for lib in u.stdlib_imports
            ).most_common(20),
            "most_common_extlib": Counter(
                lib for u in usages for lib in u.extlib_imports
            ).most_common(20),
        }

        # PR Acceptance statistics (if merge status provided)
        if pr_merge_status:
            # General: Overall acceptance
            prs_merged_total = sum(
                1 for u in usages if pr_merge_status.get(u.pr_id, False)
            )
            pct_prs_merged = 100 * prs_merged_total / total_prs if total_prs > 0 else 0

            # RQ1: PRs with imports that were merged
            prs_with_imports_merged = sum(
                1
                for u in usages
                if (u.stdlib_imports or u.extlib_imports)
                and pr_merge_status.get(u.pr_id, False)
            )
            pct_prs_with_imports_merged = (
                100 * prs_with_imports_merged / prs_with_any_import
                if prs_with_any_import > 0
                else 0
            )

            # RQ2: PRs with new deps that were merged
            prs_with_deps_merged = sum(
                1
                for u in usages
                if (u.dep_with_version or u.dep_no_version)
                and pr_merge_status.get(u.pr_id, False)
            )
            pct_prs_with_deps_merged = (
                100 * prs_with_deps_merged / prs_with_deps if prs_with_deps > 0 else 0
            )

            stats.update(
                {
                    "prs_merged_total": prs_merged_total,
                    "pct_prs_merged": pct_prs_merged,
                    "prs_with_imports_merged": prs_with_imports_merged,
                    "pct_prs_with_imports_merged": pct_prs_with_imports_merged,
                    "prs_with_deps_merged": prs_with_deps_merged,
                    "pct_prs_with_deps_merged": pct_prs_with_deps_merged,
                }
            )

        return stats
