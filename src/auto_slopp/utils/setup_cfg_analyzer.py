"""Utility for fetching and parsing setup.cfg files from popular Python packages."""

import configparser
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

logger = logging.getLogger(__name__)


@dataclass
class SetupCfgInfo:
    """Parsed information from a setup.cfg file."""

    package_name: str
    url: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)
    entry_points: Dict[str, List[str]] = field(default_factory=dict)
    raw_content: str = ""
    error: Optional[str] = None


POPULAR_PACKAGES_SETUP_CFG = [
    (
        "setuptools",
        "https://github.com/pypa/setuptools/raw/52c990172fec37766b3566679724aa8bf70ae06d/setup.cfg",
    ),
    (
        "wheel",
        "https://github.com/pypa/wheel/raw/0acd203cd896afec7f715aa2ff5980a403459a3b/setup.cfg",
    ),
    (
        "importlib_metadata",
        "https://github.com/python/importlib_metadata/raw/2f05392ca980952a6960d82b2f2d2ea10aa53239/setup.cfg",
    ),
    (
        "jaraco.skeleton",
        "https://github.com/jaraco/skeleton/raw/d9008b5c510cd6969127a6a2ab6f832edddef296/setup.cfg",
    ),
    (
        "jaraco.zipp",
        "https://github.com/jaraco/zipp/raw/700d3a96390e970b6b962823bfea78b4f7e1c537/setup.cfg",
    ),
    (
        "jinja",
        "https://github.com/pallets/jinja/raw/7d72eb7fefb7dce065193967f31f805180508448/setup.cfg",
    ),
    (
        "cachetools",
        "https://github.com/tkem/cachetools/raw/2fd87a94b8d3861d80e9e4236cd480bfdd21c90d/setup.cfg",
    ),
    (
        "aiohttp",
        "https://github.com/aio-libs/aiohttp/raw/5e0e6b7080f2408d5f1dd544c0e1cf88378b7b10/setup.cfg",
    ),
    (
        "flask",
        "https://github.com/pallets/flask/raw/9486b6cf57bd6a8a261f67091aca8ca78eeec1e3/setup.cfg",
    ),
    (
        "click",
        "https://github.com/pallets/click/raw/6411f425fae545f42795665af4162006b36c5e4a/setup.cfg",
    ),
    (
        "sqlalchemy",
        "https://github.com/sqlalchemy/sqlalchemy/raw/533f5718904b620be8d63f2474229945d6f8ba5d/setup.cfg",
    ),
    (
        "pluggy",
        "https://github.com/pytest-dev/pluggy/raw/461ef63291d13589c4e21aa182cd1529257e9a0a/setup.cfg",
    ),
    (
        "pytest",
        "https://github.com/pytest-dev/pytest/raw/c7be96dae487edbd2f55b561b31b68afac1dabe6/setup.cfg",
    ),
    (
        "platformdirs",
        "https://github.com/platformdirs/platformdirs/raw/7b7852128dd6f07511b618d6edea35046bd0c6ff/setup.cfg",
    ),
    (
        "pandas",
        "https://github.com/pandas-dev/pandas/raw/bc17343f934a33dc231c8c74be95d8365537c376/setup.cfg",
    ),
    (
        "django",
        "https://github.com/django/django/raw/4e249d11a6e56ca8feb4b055b681cec457ef3a3d/setup.cfg",
    ),
    (
        "pyscaffold",
        "https://github.com/pyscaffold/pyscaffold/raw/de7aa5dc059fbd04307419c667cc4961bc9df4b8/setup.cfg",
    ),
    (
        "virtualenv",
        "https://github.com/pypa/virtualenv/raw/f92eda6e3da26a4d28c2663ffb85c4960bdb990c/setup.cfg",
    ),
]


def fetch_setup_cfg(url: str) -> Optional[str]:
    """Fetch setup.cfg content from a URL.

    Args:
        url: URL to fetch the setup.cfg from

    Returns:
        Content of the setup.cfg file or None if fetch failed
    """
    try:
        with urlopen(url, timeout=30) as response:
            return response.read().decode("utf-8")
    except (HTTPError, URLError) as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None


def parse_setup_cfg(content: str) -> configparser.ConfigParser:
    """Parse setup.cfg content into a ConfigParser.

    Args:
        content: Raw setup.cfg content

    Returns:
        Parsed ConfigParser object
    """
    parser = configparser.ConfigParser()
    parser.read_string(content)
    return parser


def extract_metadata(parser: configparser.ConfigParser) -> Dict[str, Any]:
    """Extract metadata section from parsed setup.cfg.

    Args:
        parser: Parsed ConfigParser

    Returns:
        Dictionary of metadata key-value pairs
    """
    metadata = {}
    if parser.has_section("metadata"):
        for key, value in parser.items("metadata"):
            metadata[key] = value
    return metadata


def extract_options(parser: configparser.ConfigParser) -> Dict[str, Any]:
    """Extract options section from parsed setup.cfg.

    Args:
        parser: Parsed ConfigParser

    Returns:
        Dictionary of options key-value pairs
    """
    options = {}
    if parser.has_section("options"):
        for key, value in parser.items("options"):
            options[key] = value
    return options


def extract_entry_points(parser: configparser.ConfigParser) -> Dict[str, List[str]]:
    """Extract entry points from parsed setup.cfg.

    Args:
        parser: Parsed ConfigParser

    Returns:
        Dictionary of entry point sections and their values
    """
    entry_points = {}
    for section in parser.sections():
        if section.startswith("options.entry_points") or "entry_points" in section:
            entries = []
            for key, value in parser.items(section):
                if value:
                    entries.append(f"{key} = {value}")
            if entries:
                entry_points[section] = entries
    return entry_points


def fetch_and_parse_setup_cfg(url: str, package_name: str) -> SetupCfgInfo:
    """Fetch and parse a setup.cfg file from a URL.

    Args:
        url: URL to fetch the setup.cfg from
        package_name: Name of the package

    Returns:
        SetupCfgInfo object with parsed information
    """
    result = SetupCfgInfo(package_name=package_name, url=url)

    content = fetch_setup_cfg(url)
    if content is None:
        result.error = "Failed to fetch setup.cfg"
        return result

    result.raw_content = content

    try:
        parser = parse_setup_cfg(content)
        result.metadata = extract_metadata(parser)
        result.options = extract_options(parser)
        result.entry_points = extract_entry_points(parser)
    except Exception as e:
        result.error = f"Failed to parse setup.cfg: {e}"

    return result


def fetch_all_popular_packages_setup_cfg() -> List[SetupCfgInfo]:
    """Fetch and parse setup.cfg from all popular packages.

    Returns:
        List of SetupCfgInfo objects for each package
    """
    results = []
    for package_name, url in POPULAR_PACKAGES_SETUP_CFG:
        info = fetch_and_parse_setup_cfg(url, package_name)
        results.append(info)
    return results
