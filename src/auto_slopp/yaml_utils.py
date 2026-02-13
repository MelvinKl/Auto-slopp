"""YAML utilities for configuration and data serialization."""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Load and parse a YAML file.

    Args:
        file_path: Path to the YAML file to load.

    Returns:
        Dictionary containing the parsed YAML data.

    Raises:
        FileNotFoundError: If the file does not exist.
        yaml.YAMLError: If the file contains invalid YAML.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"YAML file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(data: Dict[str, Any], file_path: Path) -> None:
    """Save data to a YAML file.

    Args:
        data: Dictionary to save as YAML.
        file_path: Path where to save the YAML file.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)


def load_yaml_optional(file_path: Path) -> Optional[Dict[str, Any]]:
    """Load YAML file if it exists, return None otherwise.

    Args:
        file_path: Path to the YAML file to load.

    Returns:
        Dictionary containing the parsed YAML data, or None if file doesn't exist.
    """
    if not file_path.exists():
        return None

    return load_yaml(file_path)
