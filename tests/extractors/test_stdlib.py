"""Unit tests for stdlib extractors."""

from src.library_extractor import LibraryExtractor


class TestStdlibDetection:
    """Test standard library detection."""

    def test_python_stdlib(self):
        """Test Python standard library detection."""
        assert LibraryExtractor.is_stdlib("os", "python")
        assert LibraryExtractor.is_stdlib("sys", "python")
        assert LibraryExtractor.is_stdlib("json", "python")
        assert LibraryExtractor.is_stdlib("pathlib", "python")
        assert not LibraryExtractor.is_stdlib("requests", "python")
        assert not LibraryExtractor.is_stdlib("numpy", "python")

    def test_javascript_stdlib(self):
        """Test JavaScript/Node.js standard library detection."""
        assert LibraryExtractor.is_stdlib("fs", "javascript")
        assert LibraryExtractor.is_stdlib("path", "javascript")
        assert LibraryExtractor.is_stdlib("http", "javascript")
        assert not LibraryExtractor.is_stdlib("express", "javascript")
        assert not LibraryExtractor.is_stdlib("react", "javascript")

    def test_typescript_stdlib(self):
        """Test TypeScript uses JavaScript stdlib."""
        assert LibraryExtractor.is_stdlib("fs", "typescript")
        assert LibraryExtractor.is_stdlib("path", "typescript")
        assert not LibraryExtractor.is_stdlib("react", "typescript")

    def test_go_stdlib(self):
        """Test Go standard library detection."""
        # Simple stdlib packages (no slash)
        assert LibraryExtractor.is_stdlib("fmt", "go")
        assert LibraryExtractor.is_stdlib("os", "go")
        assert LibraryExtractor.is_stdlib("strings", "go")

        # Stdlib with subpackages
        assert LibraryExtractor.is_stdlib("net/http", "go")
        assert LibraryExtractor.is_stdlib("encoding/json", "go")

        # External packages (have slash and not in stdlib list)
        assert not LibraryExtractor.is_stdlib("github.com/gorilla/mux", "go")
        assert not LibraryExtractor.is_stdlib("golang.org/x/crypto", "go")

    def test_unknown_language(self):
        """Test unknown language always returns False."""
        assert not LibraryExtractor.is_stdlib("anything", "unknown")
        assert not LibraryExtractor.is_stdlib("test", "ruby")
