"""
Simple configuration system for Invoice OCR Parser.

Loads configuration from YAML file and environment variables.
Provides a get_config() function for use throughout the codebase.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Union, Optional

# Default config file path
DEFAULT_CONFIG_PATH: Path = (
    Path(__file__).parent.parent.parent / "config" / "default_config.yaml"
)

# Prefix for environment variables
ENV_PREFIX: str = "OCRINVOICE_"

# Cache for loaded config
_config_cache: Dict[str, Any] = {}


def load_yaml_config(config_path: Path = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        Configuration dictionary loaded from YAML

    Raises:
        FileNotFoundError: If the config file doesn't exist
        yaml.YAMLError: If the YAML file is malformed
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def override_with_env(
    config: Dict[str, Any], prefix: str = ENV_PREFIX
) -> Dict[str, Any]:
    """
    Override config values with environment variables if present.

    Args:
        config: Configuration dictionary to modify
        prefix: Prefix for environment variable names

    Returns:
        Modified configuration dictionary with environment variable overrides
    """

    def _override(d: Dict[str, Any], parent_key: str = "") -> None:
        for key, value in d.items():
            env_key = (prefix + parent_key + key).upper().replace(".", "_")
            if isinstance(value, dict):
                _override(value, parent_key + key + "_")
            else:
                env_val = os.getenv(env_key)
                if env_val is not None:
                    d[key] = _parse_env_value(env_val)

    _override(config)
    return config


def _parse_env_value(val: str) -> Union[str, int, float, bool]:
    """
    Convert environment variable string to appropriate type.

    Args:
        val: Environment variable value as string

    Returns:
        Parsed value with appropriate type (str, int, float, or bool)
    """
    if val.lower() in ("true", "yes", "1"):
        return True
    if val.lower() in ("false", "no", "0"):
        return False

    try:
        return int(val)
    except ValueError:
        pass

    try:
        return float(val)
    except ValueError:
        pass

    return val


def validate_config(config: Dict[str, Any]) -> None:
    """
    Basic validation for required config fields.

    Args:
        config: Configuration dictionary to validate

    Raises:
        ValueError: If required sections are missing
    """
    required_sections = ["ocr", "parser", "output"]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required config section: {section}")


def get_config(reload: bool = False) -> Dict[str, Any]:
    """
    Get the application configuration as a dictionary.
    Loads from YAML and environment variables, with caching.

    Args:
        reload: Force reload of configuration (ignores cache)

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file is not found
        ValueError: If config validation fails
    """
    global _config_cache

    if not _config_cache or reload:
        config = load_yaml_config()
        config = override_with_env(config)
        validate_config(config)
        _config_cache = config

    return _config_cache
