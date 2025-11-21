"""Unit tests for integration extractors."""

from src.library_extractor import LibraryExtractor


class TestExtractFromFile:
    """Test extract_from_file method."""

    def test_python_code_file(self):
        """Test extracting from Python code file."""
        content = "import requests\nfrom flask import Flask"
        result = LibraryExtractor.extract_from_file("main.py", content, "python")
        assert result == {"requests", "flask"}

    def test_python_requirements_file(self):
        """Test extracting from requirements.txt."""
        content = "requests==2.28.0\nflask>=2.0.0"
        result = LibraryExtractor.extract_from_file(
            "requirements.txt", content, "python"
        )
        assert result == {"requests", "flask"}

    def test_javascript_code_file(self):
        """Test extracting from JavaScript file."""
        content = "import React from 'react';\nconst express = require('express');"
        result = LibraryExtractor.extract_from_file("app.js", content, "javascript")
        assert result == {"react", "express"}

    def test_typescript_code_file(self):
        """Test extracting from TypeScript file."""
        content = "import { Component } from '@angular/core';"
        result = LibraryExtractor.extract_from_file("app.ts", content, "typescript")
        assert result == {"@angular/core"}

    def test_package_json_file(self):
        """Test extracting from package.json."""
        content = '{"dependencies": {"react": "^18.0.0"}}'
        result = LibraryExtractor.extract_from_file(
            "package.json", content, "javascript"
        )
        assert result == {"react"}

    def test_go_code_file(self):
        """Test extracting from Go file."""
        content = 'import "fmt"\nimport "github.com/gorilla/mux"'
        result = LibraryExtractor.extract_from_file("main.go", content, "go")
        assert result == {"fmt", "github.com/gorilla/mux"}

    def test_go_mod_file(self):
        """Test extracting from go.mod."""
        content = "require github.com/gorilla/mux v1.8.0"
        result = LibraryExtractor.extract_from_file("go.mod", content, "go")
        assert result == {"github.com/gorilla/mux"}

    def test_unknown_file_type(self):
        """Test unknown file type returns empty set."""
        content = "some content"
        result = LibraryExtractor.extract_from_file("unknown.txt", content, "python")
        assert result == set()

    def test_case_insensitive_filenames(self):
        """Test that filename matching is case-insensitive."""
        content = "requests==2.28.0"
        result = LibraryExtractor.extract_from_file(
            "REQUIREMENTS.TXT", content, "python"
        )
        assert result == {"requests"}
