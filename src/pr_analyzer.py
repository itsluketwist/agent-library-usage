"""Analyze pull requests for library usage patterns."""

import pandas as pd
import json
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from pathlib import Path

from .library_extractor import LibraryExtractor


@dataclass
class LibraryUsage:
    """Statistics about library usage in a PR."""
    pr_id: int
    repository_id: int
    language: str
    agent: Optional[str]

    # Libraries found
    libraries_in_code: Set[str]
    libraries_in_deps: Set[str]
    all_libraries: Set[str]

    # Classification
    new_libraries: Set[str]  # Not in stdlib, newly added
    stdlib_imports: Set[str]  # Standard library
    external_libs: Set[str]  # External, non-stdlib

    # Dependency file changes
    dep_file_added: bool
    dep_file_modified: bool
    dep_files_changed: List[str]

    # Version specifications
    libs_with_version: int
    libs_without_version: int
    version_operators: Counter

    # Statistics
    total_files_changed: int
    code_files_changed: int

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        d = asdict(self)
        # Convert sets to lists
        for key in ['libraries_in_code', 'libraries_in_deps', 'all_libraries',
                    'new_libraries', 'stdlib_imports', 'external_libs']:
            if key in d and isinstance(d[key], set):
                d[key] = list(d[key])
        # Convert Counter to dict
        if 'version_operators' in d:
            d['version_operators'] = dict(d['version_operators'])
        if 'dep_files_changed' in d:
            d['dep_files_changed'] = list(d['dep_files_changed'])
        return d


class PRAnalyzer:
    """Analyze pull requests for library usage patterns."""

    def __init__(self):
        self.extractor = LibraryExtractor()

    def analyze_commit_details(
        self,
        commit_details: pd.DataFrame,
        language: str
    ) -> Dict[int, LibraryUsage]:
        """
        Analyze commit details for library usage.

        Args:
            commit_details: DataFrame with columns: pr_id, repository_id, filename, patch, content
            language: Programming language to analyze

        Returns:
            Dictionary mapping pr_id to LibraryUsage
        """
        results = {}

        # Group by PR
        for pr_id, pr_commits in commit_details.groupby('pull_request_id'):
            usage = self._analyze_pr_commits(pr_id, pr_commits, language)
            results[pr_id] = usage

        return results

    def _analyze_pr_commits(
        self,
        pr_id: int,
        commits_df: pd.DataFrame,
        language: str
    ) -> LibraryUsage:
        """Analyze a single PR's commits for library usage."""

        # Extract basic info
        repo_id = commits_df.iloc[0]['repository_id'] if 'repository_id' in commits_df.columns else None

        # Initialize collections
        libraries_in_code = set()
        libraries_in_deps = set()
        stdlib_imports = set()
        dep_files_changed = []
        has_dep_file_add = False
        has_dep_file_modify = False

        # Version tracking
        libs_with_version = set()
        libs_without_version = set()
        version_operators = Counter()

        # Statistics
        total_files = len(commits_df)
        code_files = 0

        # Process each file change
        for _, row in commits_df.iterrows():
            filename = row.get('filename', '')
            content = row.get('content', '')
            patch = row.get('patch', '')

            if not filename:
                continue

            # Check if it's a dependency file
            is_dep_file = self._is_dependency_file(filename, language)
            is_code_file = self._is_code_file(filename, language)

            if is_dep_file:
                dep_files_changed.append(filename)

                # Check if file was added or modified
                if patch and patch.startswith('@@'):
                    has_dep_file_modify = True
                else:
                    has_dep_file_add = True

                # Extract libraries from dependency file
                dep_libs, versioned_info = self._extract_from_dep_file(
                    filename, content, language
                )
                libraries_in_deps.update(dep_libs)

                # Track version specifications
                for lib, has_version in versioned_info.items():
                    if has_version:
                        libs_with_version.add(lib)
                        # Extract operator type
                        operator = self.extractor.extract_version_operator(has_version)
                        if operator:
                            version_operators[operator] += 1
                    else:
                        libs_without_version.add(lib)

            elif is_code_file:
                code_files += 1
                # Extract libraries from code
                code_libs = self.extractor.extract_from_file(
                    filename, content, language
                )
                libraries_in_code.update(code_libs)

                # Classify as stdlib or not
                for lib in code_libs:
                    if self.extractor.is_stdlib(lib, language):
                        stdlib_imports.add(lib)

        # Combine all libraries
        all_libraries = libraries_in_code | libraries_in_deps

        # Determine external (non-stdlib) libraries
        external_libs = all_libraries - stdlib_imports

        # New libraries are those in dependency files (assumed to be newly added)
        new_libraries = libraries_in_deps.copy()

        return LibraryUsage(
            pr_id=pr_id,
            repository_id=repo_id,
            language=language,
            agent=None,  # Will be filled from PR metadata
            libraries_in_code=libraries_in_code,
            libraries_in_deps=libraries_in_deps,
            all_libraries=all_libraries,
            new_libraries=new_libraries,
            stdlib_imports=stdlib_imports,
            external_libs=external_libs,
            dep_file_added=has_dep_file_add,
            dep_file_modified=has_dep_file_modify,
            dep_files_changed=dep_files_changed,
            libs_with_version=len(libs_with_version),
            libs_without_version=len(libs_without_version),
            version_operators=version_operators,
            total_files_changed=total_files,
            code_files_changed=code_files,
        )

    def _is_dependency_file(self, filename: str, language: str) -> bool:
        """Check if a file is a dependency/package manager file."""
        filename_lower = filename.lower()
        basename = Path(filename).name.lower()

        lang_files = self.extractor.PACKAGE_FILES.get(language.lower(), [])

        for pattern in lang_files:
            if '*' in pattern:
                # Handle wildcard patterns
                pattern = pattern.replace('*', '')
                if basename.endswith(pattern):
                    return True
            else:
                if basename == pattern:
                    return True

        return False

    def _is_code_file(self, filename: str, language: str) -> bool:
        """Check if a file is a code file for the given language."""
        extensions = {
            'python': ['.py', '.pyx', '.pyi'],
            'javascript': ['.js', '.jsx', '.mjs', '.cjs'],
            'typescript': ['.ts', '.tsx'],
            'java': ['.java'],
            'go': ['.go'],
            'rust': ['.rs'],
            'ruby': ['.rb'],
            'php': ['.php'],
            'csharp': ['.cs'],
        }

        file_exts = extensions.get(language.lower(), [])
        return any(filename.endswith(ext) for ext in file_exts)

    def _extract_from_dep_file(
        self,
        filename: str,
        content: str,
        language: str
    ) -> Tuple[Set[str], Dict[str, Optional[str]]]:
        """
        Extract libraries from a dependency file.

        Returns:
            Tuple of (set of library names, dict of library -> version spec)
        """
        filename_lower = filename.lower()
        versioned_info = {}

        if language.lower() == 'python':
            if 'requirements' in filename_lower:
                pkgs = self.extractor.parse_requirements_txt(content)
                versioned_info = pkgs
                return set(pkgs.keys()), pkgs

        elif language.lower() in ['javascript', 'typescript']:
            if filename_lower.endswith('package.json'):
                pkgs = self.extractor.parse_package_json(content)
                versioned_info = pkgs
                return set(pkgs.keys()), pkgs

        elif language.lower() == 'go':
            if filename_lower == 'go.mod':
                pkgs = self.extractor.parse_go_mod(content)
                versioned_info = pkgs
                return set(pkgs.keys()), pkgs

        elif language.lower() == 'rust':
            if filename_lower.endswith('cargo.toml'):
                pkgs = self.extractor.parse_cargo_toml(content)
                versioned_info = pkgs
                return set(pkgs.keys()), pkgs

        return set(), {}

    @staticmethod
    def aggregate_statistics(usages: List[LibraryUsage]) -> Dict:
        """Aggregate statistics across multiple PR library usages."""

        total_prs = len(usages)
        if total_prs == 0:
            return {}

        stats = {
            'total_prs': total_prs,
            'prs_with_new_libs': sum(1 for u in usages if u.new_libraries),
            'prs_with_dep_changes': sum(1 for u in usages if u.dep_files_changed),
            'prs_adding_dep_file': sum(1 for u in usages if u.dep_file_added),
            'prs_modifying_dep_file': sum(1 for u in usages if u.dep_file_modified),

            # Library counts
            'total_unique_libs': len(set().union(*[u.all_libraries for u in usages])),
            'total_external_libs': len(set().union(*[u.external_libs for u in usages])),
            'total_stdlib_imports': len(set().union(*[u.stdlib_imports for u in usages])),

            # Averages
            'avg_libs_per_pr': sum(len(u.all_libraries) for u in usages) / total_prs,
            'avg_new_libs_per_pr': sum(len(u.new_libraries) for u in usages) / total_prs,
            'avg_files_changed_per_pr': sum(u.total_files_changed for u in usages) / total_prs,

            # Version specifications
            'total_libs_with_version': sum(u.libs_with_version for u in usages),
            'total_libs_without_version': sum(u.libs_without_version for u in usages),
            'version_operators': sum((u.version_operators for u in usages), Counter()),

            # Most common libraries
            'most_common_libs': Counter(
                lib for u in usages for lib in u.all_libraries
            ).most_common(20),
            'most_common_new_libs': Counter(
                lib for u in usages for lib in u.new_libraries
            ).most_common(20),
        }

        # Calculate percentages
        if stats['total_libs_with_version'] + stats['total_libs_without_version'] > 0:
            total_versioned_libs = stats['total_libs_with_version'] + stats['total_libs_without_version']
            stats['pct_libs_with_version'] = 100 * stats['total_libs_with_version'] / total_versioned_libs
        else:
            stats['pct_libs_with_version'] = 0

        stats['pct_prs_with_new_libs'] = 100 * stats['prs_with_new_libs'] / total_prs
        stats['pct_prs_with_dep_changes'] = 100 * stats['prs_with_dep_changes'] / total_prs

        return stats
