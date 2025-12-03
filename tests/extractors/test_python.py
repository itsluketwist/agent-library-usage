"""Unit tests for python extractors."""

from src.extractors import PythonExtractor


class TestPythonImportExtraction:
    """Test Python import extraction."""

    def test_simple_import(self):
        """Test simple import statements."""
        code = """
import os
import sys
import json
"""
        result = PythonExtractor.extract_imports(
            code=code,
        )
        assert result == {"os", "sys", "json"}

    def test_from_import(self):
        """Test from...import statements."""
        code = """
from pathlib import Path
from typing import Dict, List
from collections.abc import Mapping
"""
        result = PythonExtractor.extract_imports(
            code=code,
        )
        assert result == {"pathlib", "typing", "collections"}

    def test_submodule_import(self):
        """Test that only base package is extracted."""
        code = """
import os.path
import xml.etree.ElementTree
from email.mime.text import MIMEText
"""
        result = PythonExtractor.extract_imports(
            code=code,
        )
        assert result == {"os", "xml", "email"}

    def test_aliased_import(self):
        """Test imports with aliases."""
        code = """
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
"""
        result = PythonExtractor.extract_imports(
            code=code,
        )
        assert result == {"numpy", "pandas", "matplotlib"}

    def test_multiple_imports_same_line(self):
        """Test multiple imports on one line."""
        code = "import os, sys, json, re"
        result = PythonExtractor.extract_imports(
            code=code,
        )
        assert result == {"os", "sys", "json", "re"}

    def test_mixed_import_styles(self):
        """Test mixing different import styles."""
        code = """
import requests
from flask import Flask, render_template
import numpy as np
from django.db import models
"""
        result = PythonExtractor.extract_imports(
            code=code,
        )
        assert result == {"requests", "flask", "numpy", "django"}

    def test_underscore_and_dash_packages(self):
        """Test packages with underscores (Python uses underscores, not dashes)."""
        code = """
import python_dateutil
from scikit_learn import preprocessing
import some_package_name
"""
        result = PythonExtractor.extract_imports(
            code=code,
        )
        assert result == {"python_dateutil", "scikit_learn", "some_package_name"}

    def test_indented_imports(self):
        """Test imports inside functions/classes (indented)."""
        code = """
def foo():
    import tempfile
    from collections import Counter

class Bar:
    import itertools
"""
        result = PythonExtractor.extract_imports(
            code=code,
        )
        assert result == {"tempfile", "collections", "itertools"}

    def test_empty_code(self):
        """Test with empty string."""
        assert (
            PythonExtractor.extract_imports(
                code="",
            )
            == set()
        )

    def test_no_imports(self):
        """Test code without imports."""
        code = """
def hello():
    print("Hello, World!")
"""
        assert (
            PythonExtractor.extract_imports(
                code=code,
            )
            == set()
        )

    def test_relative_imports_excluded(self):
        """Test that relative imports are excluded."""
        code = """
from . import something
from .. import another
from .submodule import func
from ..parent.module import Class
import os
"""
        result = PythonExtractor.extract_imports(
            code=code,
        )
        # Should only contain os, not the relative imports
        assert result == {"os"}

    def test_multiline_relative_import(self):
        """Test that multiline relative imports don't create blank imports."""
        code = """
from .providers import (
    provider1,
    provider2,
    provider3,
)
import sys
"""
        result = PythonExtractor.extract_imports(
            code=code,
        )
        # Should only contain sys, no blank strings
        assert result == {"sys"}
        assert "" not in result


class TestRequirementsTxtParsing:
    """Test requirements.txt parsing."""

    def test_simple_packages(self):
        """Test simple package names without versions."""
        content = """
requests
flask
django
"""
        result = PythonExtractor.parse_requirements_txt(
            content=content,
        )
        assert "requests" in result
        assert "flask" in result
        assert "django" in result

    def test_version_specifiers(self):
        """Test various version specifiers."""
        content = """
requests==2.28.0
flask>=2.0.0
django<=4.0
numpy>1.20
pandas<2.0
pytest~=7.0
"""
        result = PythonExtractor.parse_requirements_txt(
            content=content,
        )
        assert result["requests"] == "==2.28.0"
        assert result["flask"] == ">=2.0.0"
        assert result["django"] == "<=4.0"
        assert result["numpy"] == ">1.20"
        assert result["pandas"] == "<2.0"
        assert result["pytest"] == "~=7.0"

    def test_comments_and_empty_lines(self):
        """Test that comments and empty lines are ignored."""
        content = """
# This is a comment
requests==2.28.0

# Another comment
flask>=2.0.0

"""
        result = PythonExtractor.parse_requirements_txt(
            content=content,
        )
        assert result == {"requests": "==2.28.0", "flask": ">=2.0.0"}

    def test_package_with_dash_and_underscore(self):
        """Test package names with dashes and underscores."""
        content = """
scikit-learn==1.0.0
python-dateutil>=2.8
some_package==1.0
my-cool_package>=2.0
"""
        result = PythonExtractor.parse_requirements_txt(
            content=content,
        )
        assert "scikit-learn" in result
        assert "python-dateutil" in result
        assert "some_package" in result
        assert "my-cool_package" in result

    def test_url_packages_ignored(self):
        """Test that URL-based packages are ignored."""
        content = """
requests==2.28.0
https://github.com/user/repo/archive/master.zip
git+https://github.com/user/repo.git
-e git+https://github.com/user/repo.git#egg=package
flask>=2.0.0
"""
        result = PythonExtractor.parse_requirements_txt(
            content=content,
        )
        assert result == {"requests": "==2.28.0", "flask": ">=2.0.0"}

    def test_complex_version_specs(self):
        """Test complex version specifications."""
        content = """
package1==1.2.3.4
package2>=1.0.0,<2.0.0
package3!=1.5.0
"""
        result = PythonExtractor.parse_requirements_txt(
            content=content,
        )
        assert result["package1"] == "==1.2.3.4"
        assert result["package2"] == ">=1.0.0,<2.0.0"
        assert result["package3"] == "!=1.5.0"


class TestPyprojectTomlParsing:
    """Test pyproject.toml parsing."""

    def test_pep621_dependencies(self):
        """Test PEP 621 style dependencies."""
        content = """
[project]
name = "my-project"
dependencies = [
    "requests>=2.28.0",
    "flask",
    "numpy==1.24.0",
]
"""
        result = PythonExtractor.parse_pyproject_toml(
            content=content,
        )
        assert result["requests"] == ">=2.28.0"
        assert result["flask"] is None
        assert result["numpy"] == "==1.24.0"

    def test_poetry_dependencies(self):
        """Test Poetry style dependencies."""
        content = """
[tool.poetry.dependencies]
python = "^3.9"
requests = "^2.28.0"
flask = ">=2.0.0"
numpy = "1.24.0"
"""
        result = PythonExtractor.parse_pyproject_toml(
            content=content,
        )
        # Python should be excluded
        assert "python" not in result
        assert result["requests"] == "^2.28.0"
        assert result["flask"] == ">=2.0.0"
        assert result["numpy"] == "1.24.0"

    def test_poetry_dict_format(self):
        """Test Poetry dict format for dependencies."""
        content = """
[tool.poetry.dependencies]
python = "^3.9"
requests = {version = "^2.28.0", extras = ["security"]}
flask = {version = ">=2.0.0"}
pandas = {git = "https://github.com/pandas-dev/pandas.git"}
"""
        result = PythonExtractor.parse_pyproject_toml(
            content=content,
        )
        assert result["requests"] == "^2.28.0"
        assert result["flask"] == ">=2.0.0"
        assert result["pandas"] is None  # No version specified for git dep

    def test_poetry_dev_dependencies(self):
        """Test Poetry dev-dependencies."""
        content = """
[tool.poetry.dependencies]
requests = "^2.28.0"

[tool.poetry.dev-dependencies]
pytest = "^7.0.0"
black = "22.10.0"
"""
        result = PythonExtractor.parse_pyproject_toml(
            content=content,
        )
        assert result["requests"] == "^2.28.0"
        assert result["pytest"] == "^7.0.0"
        assert result["black"] == "22.10.0"

    def test_mixed_pep621_and_poetry(self):
        """Test file with both PEP 621 and Poetry sections."""
        content = """
[project]
dependencies = [
    "requests>=2.28.0",
]

[tool.poetry.dependencies]
python = "^3.9"
flask = "^2.0.0"
"""
        result = PythonExtractor.parse_pyproject_toml(
            content=content,
        )
        # Both should be extracted
        assert result["requests"] == ">=2.28.0"
        assert result["flask"] == "^2.0.0"

    def test_empty_pyproject(self):
        """Test empty pyproject.toml."""
        content = """
[build-system]
requires = ["setuptools"]
"""
        result = PythonExtractor.parse_pyproject_toml(
            content=content,
        )
        assert result == {}

    def test_invalid_toml(self):
        """Test invalid TOML returns empty dict."""
        content = "this is not valid toml [[[["
        result = PythonExtractor.parse_pyproject_toml(
            content=content,
        )
        assert result == {}
