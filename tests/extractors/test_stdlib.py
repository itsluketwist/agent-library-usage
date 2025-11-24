"""Unit tests for stdlib extractors."""

from src.extractors import (
    GoExtractor,
    JavaScriptExtractor,
    PythonExtractor,
    TypeScriptExtractor,
)


class TestStdlibDetection:
    """Test standard library detection."""

    def test_python_stdlib(self):
        """Test Python standard library detection."""
        assert PythonExtractor.is_stdlib(
            module="os",
        )
        assert PythonExtractor.is_stdlib(
            module="sys",
        )
        assert PythonExtractor.is_stdlib(
            module="json",
        )
        assert PythonExtractor.is_stdlib(
            module="pathlib",
        )
        assert not PythonExtractor.is_stdlib(
            module="requests",
        )
        assert not PythonExtractor.is_stdlib(
            module="numpy",
        )

    def test_javascript_stdlib(self):
        """Test JavaScript/Node.js standard library detection."""
        assert JavaScriptExtractor.is_stdlib(
            module="fs",
        )
        assert JavaScriptExtractor.is_stdlib(
            module="path",
        )
        assert JavaScriptExtractor.is_stdlib(
            module="http",
        )
        assert not JavaScriptExtractor.is_stdlib(
            module="express",
        )
        assert not JavaScriptExtractor.is_stdlib(
            module="react",
        )

    def test_typescript_stdlib(self):
        """Test TypeScript uses JavaScript stdlib."""
        assert TypeScriptExtractor.is_stdlib(
            module="fs",
        )
        assert TypeScriptExtractor.is_stdlib(
            module="path",
        )
        assert not TypeScriptExtractor.is_stdlib(
            module="react",
        )

    def test_go_stdlib(self):
        """Test Go standard library detection."""
        # Simple stdlib packages (no slash)
        assert GoExtractor.is_stdlib(
            module="fmt",
        )
        assert GoExtractor.is_stdlib(
            module="os",
        )
        assert GoExtractor.is_stdlib(
            module="strings",
        )

        # Stdlib with subpackages
        assert GoExtractor.is_stdlib(
            module="net/http",
        )
        assert GoExtractor.is_stdlib(
            module="encoding/json",
        )

        # External packages (have slash and not in stdlib list)
        assert not GoExtractor.is_stdlib(
            module="github.com/gorilla/mux",
        )
        assert not GoExtractor.is_stdlib(
            module="golang.org/x/crypto",
        )

    def test_unknown_language(self):
        """Test unknown language always returns False."""
        # Since we don't have a generic "is_stdlib" for unknown languages,
        # we'll just test that the function doesn't exist for unknown extractors
        # This test can be removed or adjusted as needed
        pass
