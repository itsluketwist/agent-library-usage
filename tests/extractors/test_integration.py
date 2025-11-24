"""Unit tests for integration extractors."""

from src.extractors import get_extractor


class TestExtractFromFile:
    """Test extract_from_file method."""

    def test_python_code_file(self):
        """Test extracting from Python code file."""
        content = "import requests\nfrom flask import Flask"
        extractor = get_extractor(
            language="python",
        )
        file_type, result = extractor.extract_from_file(
            filename="main.py",
            content=content,
        )
        assert file_type == "code"
        assert result == {"requests": None, "flask": None}

    def test_python_requirements_file(self):
        """Test extracting from requirements.txt."""
        content = "requests==2.28.0\nflask>=2.0.0"
        extractor = get_extractor(
            language="python",
        )
        file_type, result = extractor.extract_from_file(
            filename="requirements.txt",
            content=content,
        )
        assert file_type == "dependency"
        assert result == {"requests": "==2.28.0", "flask": ">=2.0.0"}

    def test_javascript_code_file(self):
        """Test extracting from JavaScript file."""
        content = "import React from 'react';\nconst express = require('express');"
        extractor = get_extractor(
            language="javascript",
        )
        file_type, result = extractor.extract_from_file(
            filename="app.js",
            content=content,
        )
        assert file_type == "code"
        assert result == {"react": None, "express": None}

    def test_typescript_code_file(self):
        """Test extracting from TypeScript file."""
        content = "import { Component } from '@angular/core';"
        extractor = get_extractor(
            language="typescript",
        )
        file_type, result = extractor.extract_from_file(
            filename="app.ts",
            content=content,
        )
        assert file_type == "code"
        assert result == {"@angular/core": None}

    def test_package_json_file(self):
        """Test extracting from package.json."""
        content = '{"dependencies": {"react": "^18.0.0"}}'
        extractor = get_extractor(
            language="javascript",
        )
        file_type, result = extractor.extract_from_file(
            filename="package.json",
            content=content,
        )
        assert file_type == "dependency"
        assert result == {"react": "^18.0.0"}

    def test_go_code_file(self):
        """Test extracting from Go file."""
        content = 'import "fmt"\nimport "github.com/gorilla/mux"'
        extractor = get_extractor(
            language="go",
        )
        file_type, result = extractor.extract_from_file(
            filename="main.go",
            content=content,
        )
        assert file_type == "code"
        assert result == {"fmt": None, "github.com/gorilla/mux": None}

    def test_go_mod_file(self):
        """Test extracting from go.mod."""
        content = "require github.com/gorilla/mux v1.8.0"
        extractor = get_extractor(
            language="go",
        )
        file_type, result = extractor.extract_from_file(
            filename="go.mod",
            content=content,
        )
        assert file_type == "dependency"
        assert result == {"github.com/gorilla/mux": "v1.8.0"}

    def test_unknown_file_type(self):
        """Test unknown file type returns None and empty dict."""
        content = "some content"
        extractor = get_extractor(
            language="python",
        )
        file_type, result = extractor.extract_from_file(
            filename="unknown.txt",
            content=content,
        )
        assert file_type is None
        assert result == {}

    def test_case_insensitive_filenames(self):
        """Test that filename matching is case-insensitive."""
        content = "requests==2.28.0"
        extractor = get_extractor(
            language="python",
        )
        file_type, result = extractor.extract_from_file(
            filename="REQUIREMENTS.TXT",
            content=content,
        )
        assert file_type == "dependency"
        assert result == {"requests": "==2.28.0"}
