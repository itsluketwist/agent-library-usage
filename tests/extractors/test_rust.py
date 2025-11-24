"""Unit tests for Rust extractors."""

from src.library_extractor import LibraryExtractor


class TestRustImportExtraction:
    """Test Rust use statement extraction."""

    def test_simple_use(self):
        """Test simple use statements."""
        code = """
use serde;
use tokio;
use reqwest;
"""
        result = LibraryExtractor.extract_rust_imports(code)
        assert result == {"serde", "tokio", "reqwest"}

    def test_use_with_path(self):
        """Test use statements with paths."""
        code = """
use serde::Deserialize;
use tokio::runtime::Runtime;
use std::collections::HashMap;
"""
        result = LibraryExtractor.extract_rust_imports(code)
        # std should be filtered as stdlib, others should get base crate
        assert result == {"serde", "tokio"}

    def test_pub_use(self):
        """Test pub use statements."""
        code = """
pub use serde::Serialize;
pub use tokio;
"""
        result = LibraryExtractor.extract_rust_imports(code)
        assert result == {"serde", "tokio"}

    def test_use_with_braces(self):
        """Test use statements with brace groups."""
        code = """
use serde::{Serialize, Deserialize};
use tokio::{task, time};
"""
        result = LibraryExtractor.extract_rust_imports(code)
        assert result == {"serde", "tokio"}

    def test_relative_imports_excluded(self):
        """Test that relative imports (crate::, self::, super::) are excluded."""
        code = """
use crate::module;
use self::submodule;
use super::parent;
use serde;
"""
        result = LibraryExtractor.extract_rust_imports(code)
        assert result == {"serde"}

    def test_stdlib_excluded(self):
        """Test that standard library crates are excluded."""
        code = """
use std::collections::HashMap;
use std::io;
use core::fmt;
use alloc::vec::Vec;
use serde;
"""
        result = LibraryExtractor.extract_rust_imports(code)
        assert result == {"serde"}

    def test_empty_code(self):
        """Test with empty string."""
        assert LibraryExtractor.extract_rust_imports("") == set()

    def test_no_imports(self):
        """Test code without imports."""
        code = """
fn main() {
    println!("Hello, World!");
}
"""
        assert LibraryExtractor.extract_rust_imports(code) == set()


class TestCargoTomlParsing:
    """Test Cargo.toml parsing."""

    def test_simple_dependencies(self):
        """Test simple dependency format."""
        content = """
[dependencies]
serde = "1.0"
tokio = "1.25"
reqwest = "0.11"
"""
        result = LibraryExtractor.parse_cargo_toml(content)
        assert result == {
            "serde": "1.0",
            "tokio": "1.25",
            "reqwest": "0.11",
        }

    def test_table_format_inline(self):
        """Test table format dependencies (inline)."""
        content = """
[dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.25", features = ["full"] }
"""
        result = LibraryExtractor.parse_cargo_toml(content)
        assert result["serde"] == "1.0"
        assert result["tokio"] == "1.25"

    def test_dev_dependencies(self):
        """Test dev-dependencies section."""
        content = """
[dependencies]
serde = "1.0"

[dev-dependencies]
tokio-test = "0.4"
criterion = "0.5"
"""
        result = LibraryExtractor.parse_cargo_toml(content)
        assert "serde" in result
        assert "tokio-test" in result
        assert "criterion" in result

    def test_build_dependencies(self):
        """Test build-dependencies section."""
        content = """
[dependencies]
serde = "1.0"

[build-dependencies]
cc = "1.0"
"""
        result = LibraryExtractor.parse_cargo_toml(content)
        assert "serde" in result
        assert "cc" in result

    def test_mixed_sections(self):
        """Test multiple dependency sections."""
        content = """
[package]
name = "my-app"
version = "0.1.0"

[dependencies]
serde = "1.0"
tokio = "1.25"

[dev-dependencies]
criterion = "0.5"

[build-dependencies]
cc = "1.0"
"""
        result = LibraryExtractor.parse_cargo_toml(content)
        assert len(result) == 4
        assert "serde" in result
        assert "tokio" in result
        assert "criterion" in result
        assert "cc" in result

    def test_empty_dependencies(self):
        """Test Cargo.toml with no dependencies."""
        content = """
[package]
name = "my-app"
version = "0.1.0"
"""
        result = LibraryExtractor.parse_cargo_toml(content)
        assert result == {}


class TestRustStdlibDetection:
    """Test Rust standard library detection."""

    def test_stdlib_crates(self):
        """Test standard library crate detection."""
        assert LibraryExtractor.is_stdlib("std", "rust")
        assert LibraryExtractor.is_stdlib("core", "rust")
        assert LibraryExtractor.is_stdlib("alloc", "rust")
        assert LibraryExtractor.is_stdlib("proc_macro", "rust")

    def test_external_crates(self):
        """Test external crate detection."""
        assert not LibraryExtractor.is_stdlib("serde", "rust")
        assert not LibraryExtractor.is_stdlib("tokio", "rust")
        assert not LibraryExtractor.is_stdlib("reqwest", "rust")
