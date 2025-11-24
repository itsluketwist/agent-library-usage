"""Unit tests for go extractors."""

from src.extractors import GoExtractor


class TestGoImportExtraction:
    """Test Go import extraction."""

    def test_single_import(self):
        """Test single import statement."""
        code = """
package main

import "fmt"
import "os"
import "strings"
"""
        result = GoExtractor.extract_imports(
            code=code,
        )
        assert result == {"fmt", "os", "strings"}

    def test_multi_import_block(self):
        """Test multi-line import block."""
        code = """
package main

import (
    "fmt"
    "os"
    "net/http"
    "encoding/json"
)
"""
        result = GoExtractor.extract_imports(
            code=code,
        )
        assert result == {"fmt", "os", "net/http", "encoding/json"}

    def test_external_packages(self):
        """Test external package imports (github.com, etc.)."""
        code = """
import (
    "fmt"
    "github.com/gorilla/mux"
    "github.com/stretchr/testify/assert"
    "golang.org/x/crypto/bcrypt"
)
"""
        result = GoExtractor.extract_imports(
            code=code,
        )
        assert result == {
            "fmt",
            "github.com/gorilla/mux",
            "github.com/stretchr/testify",
            "golang.org/x/crypto",
        }

    def test_aliased_imports(self):
        """Test aliased imports (should still extract package path)."""
        code = """
import (
    _ "github.com/lib/pq"
    . "github.com/onsi/ginkgo"
    mux "github.com/gorilla/mux"
)
"""
        result = GoExtractor.extract_imports(
            code=code,
        )
        # Note: Our current implementation doesn't handle aliases,
        # but it should at least get the package paths
        assert "github.com/lib/pq" in result
        assert "github.com/onsi/ginkgo" in result
        assert "github.com/gorilla/mux" in result

    def test_stdlib_subpackages(self):
        """Test standard library subpackages."""
        code = """
import (
    "net/http"
    "net/url"
    "encoding/json"
    "encoding/xml"
    "text/template"
)
"""
        result = GoExtractor.extract_imports(
            code=code,
        )
        assert result == {
            "net/http",
            "net/url",
            "encoding/json",
            "encoding/xml",
            "text/template",
        }

    def test_mixed_import_styles(self):
        """Test mixing single and block imports."""
        code = """
package main

import "fmt"

import (
    "os"
    "strings"
)

import "net/http"
"""
        result = GoExtractor.extract_imports(
            code=code,
        )
        assert result == {"fmt", "os", "strings", "net/http"}

    def test_empty_import_block(self):
        """Test handling of empty or malformed imports."""
        code = """
import ()

import (
)
"""
        result = GoExtractor.extract_imports(
            code=code,
        )
        assert result == set()


class TestGoModParsing:
    """Test go.mod parsing."""

    def test_require_block(self):
        """Test parsing require block."""
        content = """
module myapp

go 1.19

require (
    github.com/gorilla/mux v1.8.0
    github.com/stretchr/testify v1.8.0
    golang.org/x/crypto v0.5.0
)
"""
        result = GoExtractor.parse_go_mod(
            content=content,
        )
        assert result == {
            "github.com/gorilla/mux": "v1.8.0",
            "github.com/stretchr/testify": "v1.8.0",
            "golang.org/x/crypto": "v0.5.0",
        }

    def test_single_require(self):
        """Test single require statements."""
        content = """
module myapp

require github.com/gorilla/mux v1.8.0
require github.com/pkg/errors v0.9.1
"""
        result = GoExtractor.parse_go_mod(
            content=content,
        )
        assert result == {
            "github.com/gorilla/mux": "v1.8.0",
            "github.com/pkg/errors": "v0.9.1",
        }

    def test_mixed_require_styles(self):
        """Test mixing require block and single requires."""
        content = """
module myapp

require github.com/pkg/errors v0.9.1

require (
    github.com/gorilla/mux v1.8.0
    github.com/stretchr/testify v1.8.0
)

require golang.org/x/crypto v0.5.0
"""
        result = GoExtractor.parse_go_mod(
            content=content,
        )
        assert len(result) == 4
        assert "github.com/pkg/errors" in result
        assert "github.com/gorilla/mux" in result
        assert "github.com/stretchr/testify" in result
        assert "golang.org/x/crypto" in result

    def test_indirect_dependencies(self):
        """Test indirect dependencies (should still be captured)."""
        content = """
require (
    github.com/gorilla/mux v1.8.0 // indirect
    github.com/stretchr/testify v1.8.0
)
"""
        result = GoExtractor.parse_go_mod(
            content=content,
        )
        assert "github.com/gorilla/mux" in result
        assert "github.com/stretchr/testify" in result

    def test_replace_directives_ignored(self):
        """Test that replace directives are not parsed as requires."""
        content = """
require github.com/gorilla/mux v1.8.0

replace github.com/old/module => github.com/new/module v1.0.0
"""
        result = GoExtractor.parse_go_mod(
            content=content,
        )
        # Should only get the required package, not the replaced one
        assert "github.com/gorilla/mux" in result
        assert len(result) == 1
