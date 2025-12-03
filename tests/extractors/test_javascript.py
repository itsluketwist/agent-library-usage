"""Unit tests for javascript extractors."""

from src.extractors import JavaScriptExtractor, TypeScriptExtractor


class TestJavaScriptImportExtraction:
    """Test JavaScript/TypeScript import extraction."""

    def test_es6_import(self):
        """Test ES6 import statements."""
        code = """
import React from 'react';
import { useState, useEffect } from 'react';
import * as utils from 'lodash';
"""
        result = JavaScriptExtractor.extract_imports(
            code=code,
        )
        assert result == {"react", "lodash"}

    def test_require_import(self):
        """Test CommonJS require statements."""
        code = """
const express = require('express');
const fs = require('fs');
const axios = require('axios');
"""
        result = JavaScriptExtractor.extract_imports(
            code=code,
        )
        assert result == {"express", "fs", "axios"}

    def test_scoped_packages(self):
        """Test scoped packages (@org/package)."""
        code = """
import { Component } from '@angular/core';
import { Button } from '@mui/material';
const babel = require('@babel/core');
"""
        result = JavaScriptExtractor.extract_imports(
            code=code,
        )
        assert result == {"@angular/core", "@mui/material", "@babel/core"}

    def test_subpath_imports(self):
        """Test imports with subpaths."""
        code = """
import Button from 'antd/lib/button';
import 'lodash/fp/map';
const router = require('express/lib/router');
"""
        result = JavaScriptExtractor.extract_imports(
            code=code,
        )
        assert result == {"antd", "lodash", "express"}

    def test_relative_imports_excluded(self):
        """Test that relative imports are excluded."""
        code = """
import './styles.css';
import { helper } from '../utils/helper';
import config from '../../config';
const local = require('./local');
"""
        result = JavaScriptExtractor.extract_imports(
            code=code,
        )
        assert result == set()

    def test_mixed_quotes(self):
        """Test both single and double quotes."""
        code = """
import react from "react";
import vue from 'vue';
const axios = require("axios");
const lodash = require('lodash');
"""
        result = JavaScriptExtractor.extract_imports(
            code=code,
        )
        assert result == {"react", "vue", "axios", "lodash"}

    def test_package_with_dash(self):
        """Test packages with dashes."""
        code = """
import moment from 'moment-timezone';
const parser = require('body-parser');
import validator from 'express-validator';
"""
        result = JavaScriptExtractor.extract_imports(
            code=code,
        )
        assert result == {"moment-timezone", "body-parser", "express-validator"}

    def test_type_imports(self):
        """Test TypeScript type imports."""
        code = """
import type { User } from 'user-types';
import { type Config } from 'config-types';
"""
        result = JavaScriptExtractor.extract_imports(
            code=code,
        )
        assert result == {"user-types", "config-types"}

    def test_typescript_uses_js_extractor(self):
        """Test that TypeScript extraction uses JS extraction."""
        code = "import React from 'react';"
        result = TypeScriptExtractor.extract_imports(
            code=code,
        )
        assert result == {"react"}

    def test_path_alias_excluded(self):
        """Test that @/ path aliases are excluded."""
        code = """
import { Component } from '@/components/ui/button'
import { lib } from '@/lib/utils'
import { hook } from '@/hooks/useData'
import React from 'react'
import { toast } from 'sonner'
"""
        result = JavaScriptExtractor.extract_imports(
            code=code,
        )
        assert result == {"react", "sonner"}
        assert "@/components" not in result
        assert "@/lib" not in result
        assert "@/hooks" not in result


class TestPackageJsonParsing:
    """Test package.json parsing."""

    def test_dependencies(self):
        """Test parsing dependencies."""
        content = """
{
  "dependencies": {
    "react": "^18.0.0",
    "lodash": "~4.17.21",
    "axios": "^1.0.0"
  }
}
"""
        result = JavaScriptExtractor.parse_package_json(
            content=content,
        )
        assert result == {
            "react": "^18.0.0",
            "lodash": "~4.17.21",
            "axios": "^1.0.0",
        }

    def test_dev_dependencies(self):
        """Test parsing devDependencies."""
        content = """
{
  "devDependencies": {
    "jest": "^29.0.0",
    "eslint": "^8.0.0"
  }
}
"""
        result = JavaScriptExtractor.parse_package_json(
            content=content,
        )
        assert result == {"jest": "^29.0.0", "eslint": "^8.0.0"}

    def test_peer_dependencies(self):
        """Test parsing peerDependencies."""
        content = """
{
  "peerDependencies": {
    "react": ">=16.8.0",
    "react-dom": ">=16.8.0"
  }
}
"""
        result = JavaScriptExtractor.parse_package_json(
            content=content,
        )
        assert result == {"react": ">=16.8.0", "react-dom": ">=16.8.0"}

    def test_all_dependency_types(self):
        """Test combining all dependency types."""
        content = """
{
  "dependencies": {
    "react": "^18.0.0"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  },
  "peerDependencies": {
    "typescript": "^5.0.0"
  }
}
"""
        result = JavaScriptExtractor.parse_package_json(
            content=content,
        )
        assert result == {
            "react": "^18.0.0",
            "jest": "^29.0.0",
            "typescript": "^5.0.0",
        }

    def test_scoped_packages(self):
        """Test scoped packages."""
        content = """
{
  "dependencies": {
    "@angular/core": "^15.0.0",
    "@mui/material": "^5.0.0",
    "@babel/core": "^7.0.0"
  }
}
"""
        result = JavaScriptExtractor.parse_package_json(
            content=content,
        )
        assert "@angular/core" in result
        assert "@mui/material" in result
        assert "@babel/core" in result

    def test_package_with_dash(self):
        """Test packages with dashes."""
        content = """
{
  "dependencies": {
    "body-parser": "^1.20.0",
    "express-validator": "^6.14.0"
  }
}
"""
        result = JavaScriptExtractor.parse_package_json(
            content=content,
        )
        assert "body-parser" in result
        assert "express-validator" in result

    def test_invalid_json(self):
        """Test handling of invalid JSON."""
        content = "{ invalid json }"
        result = JavaScriptExtractor.parse_package_json(
            content=content,
        )
        assert result == {}

    def test_empty_dependencies(self):
        """Test package.json with no dependencies."""
        content = '{"name": "my-app", "version": "1.0.0"}'
        result = JavaScriptExtractor.parse_package_json(
            content=content,
        )
        assert result == {}
