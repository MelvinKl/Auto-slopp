"""YAML configuration file loader."""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Dictionary containing the configuration values.

    Raises:
        FileNotFoundError: If the config file doesn't exist.
        yaml.YAMLError: If the YAML file is malformed.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if config is None:
        return {}

    if not isinstance(config, dict):
        raise ValueError(f"Configuration file must contain a dictionary, got {type(config).__name__}")

    return config


def get_config_value(config: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Get a configuration value from a nested dictionary using dot notation.

    Args:
        config: Configuration dictionary.
        key: Key to retrieve (supports dot notation, e.g., "section.nested.key").
        default: Default value if key not found.

    Returns:
        The configuration value or default.
    """
    keys = key.split(".")
    value = config

    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default

    return value
