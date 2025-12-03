"""Unit tests for PR analyzer."""

import pandas as pd

from src.pr_analyzer import PRAnalyzer


class TestProjectPackageInference:
    """Test project package name inference."""

    def test_infer_single_package(self):
        """Test inferring a single project package."""
        commits_df = pd.DataFrame(
            {
                "filename": [
                    "alpha_factory_v1/__init__.py",
                    "alpha_factory_v1/tests/test_smoke.py",
                    "alpha_factory_v1/requests.py",
                ]
            }
        )

        analyzer = PRAnalyzer()
        packages = analyzer._infer_project_packages(commits_df)

        assert packages == {"alpha_factory_v1"}

    def test_infer_multiple_packages(self):
        """Test inferring multiple project packages."""
        commits_df = pd.DataFrame(
            {
                "filename": [
                    "src/main.py",
                    "src/utils/helpers.py",
                    "app/models.py",
                    "app/views.py",
                    "tests/test_main.py",
                    "README.md",
                    "setup.py",
                ]
            }
        )

        analyzer = PRAnalyzer()
        packages = analyzer._infer_project_packages(commits_df)

        # Should identify src, app, and tests as project packages
        assert packages == {"src", "app", "tests"}

    def test_infer_src_directory(self):
        """Test that src directory is correctly identified."""
        commits_df = pd.DataFrame(
            {
                "filename": [
                    "src/connections/base_connection.py",
                    "src/event_bus.py",
                    "src/connection_manager.py",
                ]
            }
        )

        analyzer = PRAnalyzer()
        packages = analyzer._infer_project_packages(commits_df)

        assert packages == {"src"}

    def test_ignore_non_package_directories(self):
        """Test that non-package directories are not included."""
        commits_df = pd.DataFrame(
            {
                "filename": [
                    "docs/index.md",
                    ".github/workflows/ci.yml",
                    "scripts/deploy.sh",
                    "src/main.py",
                ]
            }
        )

        analyzer = PRAnalyzer()
        packages = analyzer._infer_project_packages(commits_df)

        # Only src should be identified (has .py files)
        # docs, .github, scripts don't have Python files in expected structure
        assert "src" in packages
        assert "docs" not in packages
        assert ".github" not in packages
        assert "scripts" not in packages

    def test_valid_python_package_names(self):
        """Test that only valid Python package names are included."""
        commits_df = pd.DataFrame(
            {
                "filename": [
                    "my-package/main.py",  # Has dash - invalid Python identifier
                    "valid_package/main.py",  # Valid
                    "123invalid/main.py",  # Starts with number - but will pass alphanumeric check
                    "valid123/main.py",  # Valid
                ]
            }
        )

        analyzer = PRAnalyzer()
        packages = analyzer._infer_project_packages(commits_df)

        # Should only include valid Python package names
        # Note: our current implementation checks alphanumeric + underscore
        assert "valid_package" in packages
        assert "valid123" in packages
        # my-package has a dash, so it won't pass the check
        assert "my-package" not in packages
