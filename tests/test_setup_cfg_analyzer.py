"""Tests for setup_cfg_analyzer utility and worker."""

from unittest.mock import patch

import pytest

from auto_slopp.utils.setup_cfg_analyzer import (
    POPULAR_PACKAGES_SETUP_CFG,
    SetupCfgInfo,
    extract_entry_points,
    extract_metadata,
    extract_options,
    fetch_and_parse_setup_cfg,
    fetch_setup_cfg,
    parse_setup_cfg,
)


class TestFetchSetupCfg:
    """Tests for fetch_setup_cfg function."""

    @patch("auto_slopp.utils.setup_cfg_analyzer.urlopen")
    def test_fetch_setup_cfg_success(self, mock_urlopen):
        """Test successful fetch of setup.cfg."""
        mock_response = b"[metadata]\nname = test-package\nversion = 1.0.0"
        mock_context = mock_urlopen.return_value.__enter__.return_value
        mock_context.read.return_value = mock_response

        result = fetch_setup_cfg("https://example.com/setup.cfg")

        assert result is not None
        assert "metadata" in result

    @patch("auto_slopp.utils.setup_cfg_analyzer.urlopen")
    def test_fetch_setup_cfg_failure(self, mock_urlopen):
        """Test failed fetch returns None."""
        from urllib.error import URLError

        mock_urlopen.side_effect = URLError("Connection failed")

        result = fetch_setup_cfg("https://example.com/setup.cfg")

        assert result is None


class TestParseSetupCfg:
    """Tests for parse_setup_cfg function."""

    def test_parse_simple_setup_cfg(self):
        """Test parsing a simple setup.cfg."""
        content = """[metadata]
name = test-package
version = 1.0.0

[options]
packages = find
"""
        parser = parse_setup_cfg(content)

        assert parser.has_section("metadata")
        assert parser.has_section("options")
        assert parser.get("metadata", "name") == "test-package"
        assert parser.get("metadata", "version") == "1.0.0"


class TestExtractMetadata:
    """Tests for extract_metadata function."""

    def test_extract_metadata_basic(self):
        """Test extracting basic metadata."""
        content = """[metadata]
name = test-package
author = Test Author
version = 1.0.0
"""
        parser = parse_setup_cfg(content)
        metadata = extract_metadata(parser)

        assert metadata["name"] == "test-package"
        assert metadata["author"] == "Test Author"
        assert metadata["version"] == "1.0.0"

    def test_extract_metadata_empty(self):
        """Test extracting metadata from config without metadata section."""
        content = """[options]
packages = find
"""
        parser = parse_setup_cfg(content)
        metadata = extract_metadata(parser)

        assert metadata == {}


class TestExtractOptions:
    """Tests for extract_options function."""

    def test_extract_options_basic(self):
        """Test extracting basic options."""
        content = """[options]
packages = find
python_requires = >=3.7
"""
        parser = parse_setup_cfg(content)
        options = extract_options(parser)

        assert options["packages"] == "find"
        assert options["python_requires"] == ">=3.7"


class TestExtractEntryPoints:
    """Tests for extract_entry_points function."""

    def test_extract_entry_points_console_scripts(self):
        """Test extracting console_scripts entry points."""
        content = """[options.entry_points]
console_scripts =
    mycmd = mypackage.cli:main
"""
        parser = parse_setup_cfg(content)
        entry_points = extract_entry_points(parser)

        assert "options.entry_points" in entry_points

    def test_extract_entry_points_empty(self):
        """Test extracting entry points when none exist."""
        content = """[metadata]
name = test-package
"""
        parser = parse_setup_cfg(content)
        entry_points = extract_entry_points(parser)

        assert entry_points == {}


class TestSetupCfgInfo:
    """Tests for SetupCfgInfo dataclass."""

    def test_setup_cfg_info_creation(self):
        """Test creating a SetupCfgInfo object."""
        info = SetupCfgInfo(
            package_name="test-package",
            url="https://example.com/setup.cfg",
            metadata={"name": "test"},
            options={"packages": "find"},
            entry_points={"console_scripts": ["test = main"]},
        )

        assert info.package_name == "test-package"
        assert info.metadata == {"name": "test"}
        assert info.options == {"packages": "find"}
        assert info.entry_points == {"console_scripts": ["test = main"]}

    def test_setup_cfg_info_with_error(self):
        """Test SetupCfgInfo with error."""
        info = SetupCfgInfo(
            package_name="test-package",
            url="https://example.com/setup.cfg",
            error="Failed to fetch",
        )

        assert info.error == "Failed to fetch"


class TestPopularPackagesList:
    """Tests for POPULAR_PACKAGES_SETUP_CFG list."""

    def test_popular_packages_not_empty(self):
        """Test that popular packages list is not empty."""
        assert len(POPULAR_PACKAGES_SETUP_CFG) > 0

    def test_popular_packages_format(self):
        """Test that popular packages have correct format."""
        for package_name, url in POPULAR_PACKAGES_SETUP_CFG:
            assert isinstance(package_name, str)
            assert isinstance(url, str)
            assert url.startswith("https://github.com/")
            assert url.endswith("setup.cfg")

    def test_expected_packages_present(self):
        """Test that expected packages are in the list."""
        package_names = [name for name, _ in POPULAR_PACKAGES_SETUP_CFG]

        expected = ["setuptools", "wheel", "pytest", "flask", "django"]
        for pkg in expected:
            assert pkg in package_names
