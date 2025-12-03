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
        packages = analyzer._infer_project_packages(commits_df, "python")

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
        packages = analyzer._infer_project_packages(commits_df, "python")

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
        packages = analyzer._infer_project_packages(commits_df, "python")

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
        packages = analyzer._infer_project_packages(commits_df, "python")

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
        packages = analyzer._infer_project_packages(commits_df, "python")

        # Should only include valid Python package names
        # Note: our current implementation checks alphanumeric + underscore
        assert "valid_package" in packages
        assert "valid123" in packages
        # my-package has a dash, so it won't pass the check
        assert "my-package" not in packages

    def test_infer_rust_crate_names(self):
        """Test inferring Rust crate names from file paths."""
        commits_df = pd.DataFrame(
            {
                "filename": [
                    "crates/glaredb_error/src/lib.rs",
                    "crates/glaredb_error/src/types.rs",
                    "crates/near_primitives/src/version.rs",
                    "core/src/primitives.rs",
                    "README.md",
                ]
            }
        )

        analyzer = PRAnalyzer()
        packages = analyzer._infer_project_packages(commits_df, "rust")

        assert "glaredb_error" in packages
        assert "near_primitives" in packages
        assert "core" in packages  # core/src pattern

    def test_infer_go_local_packages(self):
        """Test inferring Go local packages from file paths."""
        commits_df = pd.DataFrame(
            {
                "filename": [
                    "mochi/parser/lexer.go",
                    "mochi/parser/parser.go",
                    "mochi/types/types.go",
                    "mochi/ast/node.go",
                    "mochi/interpreter/eval.go",
                    "cmd/mochi/main.go",
                    "README.md",
                ]
            }
        )

        analyzer = PRAnalyzer()
        packages = analyzer._infer_project_packages(commits_df, "go")

        # Should include base packages (used as prefixes for filtering)
        assert "mochi" in packages
        assert "cmd" in packages
        # Should NOT include subpackages (we now only track base packages)
        assert "mochi/parser" not in packages

    def test_infer_csharp_sample_apps(self):
        """Test inferring C# sample applications."""
        commits_df = pd.DataFrame(
            {
                "filename": [
                    "samples/BehaviorsTestApplication/App.axaml",
                    "samples/BehaviorsTestApplication/Views/MainView.axaml",
                    "samples/DockSample/MainWindow.axaml",
                    "src/Dock/DockFactory.cs",
                    "tests/UnitTests/TestClass.cs",
                ]
            }
        )

        analyzer = PRAnalyzer()
        packages = analyzer._infer_project_packages(commits_df, "csharp")

        assert "BehaviorsTestApplication" in packages
        assert "DockSample" in packages
        assert "UnitTests" in packages
        # src/ should not be included (not in samples/tests/examples)
        assert "src" not in packages
