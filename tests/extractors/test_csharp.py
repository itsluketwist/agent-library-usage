"""Unit tests for C# extractors."""

from src.library_extractor import LibraryExtractor


class TestCSharpImportExtraction:
    """Test C# using statement extraction."""

    def test_simple_using(self):
        """Test simple using statements."""
        code = """
using System;
using System.Collections;
using System.Linq;
"""
        result = LibraryExtractor.extract_csharp_imports(code)
        assert result == {"System"}

    def test_using_with_namespaces(self):
        """Test using statements with nested namespaces."""
        code = """
using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;
using Microsoft.AspNetCore;
"""
        result = LibraryExtractor.extract_csharp_imports(code)
        assert result == {"System", "Newtonsoft", "Microsoft"}

    def test_mixed_using(self):
        """Test mixing different namespace patterns."""
        code = """
using System;
using System.Linq;
using Newtonsoft.Json;
using Serilog;
using AutoMapper;
"""
        result = LibraryExtractor.extract_csharp_imports(code)
        assert result == {"System", "Newtonsoft", "Serilog", "AutoMapper"}

    def test_indented_using(self):
        """Test using statements inside namespaces."""
        code = """
namespace MyApp
{
    using System;
    using System.Linq;
}
"""
        result = LibraryExtractor.extract_csharp_imports(code)
        # Our regex should catch indented using statements
        assert "System" in result

    def test_empty_code(self):
        """Test with empty string."""
        assert LibraryExtractor.extract_csharp_imports("") == set()

    def test_no_imports(self):
        """Test code without using statements."""
        code = """
namespace MyApp
{
    public class Program
    {
        static void Main(string[] args)
        {
        }
    }
}
"""
        assert LibraryExtractor.extract_csharp_imports(code) == set()


class TestCsprojParsing:
    """Test .csproj file parsing."""

    def test_simple_package_references(self):
        """Test simple PackageReference entries."""
        content = """
<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="13.0.1" />
    <PackageReference Include="Serilog" Version="2.12.0" />
  </ItemGroup>
</Project>
"""
        result = LibraryExtractor.parse_csproj(content)
        assert result == {
            "Newtonsoft.Json": "13.0.1",
            "Serilog": "2.12.0",
        }

    def test_package_reference_with_child_element(self):
        """Test PackageReference with Version as child element."""
        content = """
<Project>
  <ItemGroup>
    <PackageReference Include="EntityFramework">
      <Version>6.4.4</Version>
    </PackageReference>
  </ItemGroup>
</Project>
"""
        result = LibraryExtractor.parse_csproj(content)
        assert "EntityFramework" in result
        assert result["EntityFramework"] == "6.4.4"

    def test_package_reference_without_version(self):
        """Test PackageReference without version."""
        content = """
<Project>
  <ItemGroup>
    <PackageReference Include="MyLocalPackage" />
  </ItemGroup>
</Project>
"""
        result = LibraryExtractor.parse_csproj(content)
        assert "MyLocalPackage" in result
        assert result["MyLocalPackage"] is None

    def test_multiple_itemgroups(self):
        """Test multiple ItemGroup sections."""
        content = """
<Project>
  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="13.0.1" />
  </ItemGroup>
  <ItemGroup>
    <PackageReference Include="Serilog" Version="2.12.0" />
  </ItemGroup>
</Project>
"""
        result = LibraryExtractor.parse_csproj(content)
        assert len(result) == 2
        assert "Newtonsoft.Json" in result
        assert "Serilog" in result

    def test_empty_project(self):
        """Test .csproj with no package references."""
        content = """
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net6.0</TargetFramework>
  </PropertyGroup>
</Project>
"""
        result = LibraryExtractor.parse_csproj(content)
        assert result == {}


class TestPackagesConfigParsing:
    """Test packages.config parsing."""

    def test_simple_packages(self):
        """Test simple package entries."""
        content = """
<?xml version="1.0" encoding="utf-8"?>
<packages>
  <package id="Newtonsoft.Json" version="13.0.1" targetFramework="net472" />
  <package id="Serilog" version="2.12.0" targetFramework="net472" />
</packages>
"""
        result = LibraryExtractor.parse_packages_config(content)
        assert result == {
            "Newtonsoft.Json": "13.0.1",
            "Serilog": "2.12.0",
        }

    def test_package_without_version(self):
        """Test package without version attribute."""
        content = """
<packages>
  <package id="MyPackage" targetFramework="net472" />
</packages>
"""
        result = LibraryExtractor.parse_packages_config(content)
        assert "MyPackage" in result
        assert result["MyPackage"] is None

    def test_empty_packages(self):
        """Test packages.config with no packages."""
        content = """
<?xml version="1.0" encoding="utf-8"?>
<packages>
</packages>
"""
        result = LibraryExtractor.parse_packages_config(content)
        assert result == {}


class TestPaketDependenciesParsing:
    """Test paket.dependencies parsing."""

    def test_simple_dependencies(self):
        """Test simple nuget dependencies."""
        content = """
source https://api.nuget.org/v3/index.json

nuget Newtonsoft.Json 13.0.1
nuget Serilog 2.12.0
nuget FSharp.Core
"""
        result = LibraryExtractor.parse_packages_config(content)
        # Note: parse_packages_config doesn't handle paket format
        # We'd use parse_paket_dependencies if implemented
        # This test is a placeholder


class TestCSharpStdlibDetection:
    """Test C# standard library detection."""

    def test_system_namespace(self):
        """Test System namespace detection."""
        assert LibraryExtractor.is_stdlib("System", "csharp")

    def test_microsoft_namespace(self):
        """Test Microsoft namespace detection."""
        assert LibraryExtractor.is_stdlib("Microsoft", "csharp")

    def test_external_packages(self):
        """Test external package detection."""
        assert not LibraryExtractor.is_stdlib("Newtonsoft", "csharp")
        assert not LibraryExtractor.is_stdlib("Serilog", "csharp")
        assert not LibraryExtractor.is_stdlib("AutoMapper", "csharp")
