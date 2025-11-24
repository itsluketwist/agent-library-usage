"""Analyse pull requests for library usage patterns."""

from collections import Counter
from dataclasses import dataclass

import pandas as pd

from .extractors import get_extractor


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
                    if extractor_class.is_stdlib(module=lib):
                        stdlib_imports.add(lib)
                    else:
                        extlib_imports.add(lib)
            elif file_type == "dependency":
                # Dependency file: categorize by whether version is specified
                for lib, version in libs_dict.items():
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
    ) -> dict[str, int | float | list[tuple[str, int]]]:
        """Aggregate statistics across multiple PR library usages."""

        total_prs = len(usages)
        if total_prs == 0:
            return {}

        # Count unique libraries across all PRs
        all_stdlib = set().union(*[u.stdlib_imports for u in usages])
        all_extlib = set().union(*[u.extlib_imports for u in usages])
        all_dep_with_ver = set().union(*[u.dep_with_version for u in usages])
        all_dep_no_ver = set().union(*[u.dep_no_version for u in usages])

        # Count PRs with dependencies
        prs_with_deps = sum(1 for u in usages if u.dep_with_version or u.dep_no_version)

        stats = {
            "total_prs": total_prs,
            # Import counts
            "total_stdlib_imports": len(all_stdlib),
            "total_extlib_imports": len(all_extlib),
            # Dependency counts
            "total_deps_with_version": len(all_dep_with_ver),
            "total_deps_without_version": len(all_dep_no_ver),
            # PRs with dependencies
            "prs_with_deps": prs_with_deps,
            "pct_prs_with_deps": 100 * prs_with_deps / total_prs
            if total_prs > 0
            else 0,
            # Averages
            "avg_stdlib_per_pr": sum(len(u.stdlib_imports) for u in usages) / total_prs,
            "avg_extlib_per_pr": sum(len(u.extlib_imports) for u in usages) / total_prs,
            "avg_deps_per_pr": sum(
                len(u.dep_with_version) + len(u.dep_no_version) for u in usages
            )
            / total_prs,
            # Most common
            "most_common_stdlib": Counter(
                lib for u in usages for lib in u.stdlib_imports
            ).most_common(20),
            "most_common_extlib": Counter(
                lib for u in usages for lib in u.extlib_imports
            ).most_common(20),
            "most_common_deps": Counter(
                lib for u in usages for lib in u.dep_with_version | u.dep_no_version
            ).most_common(20),
        }

        return stats
