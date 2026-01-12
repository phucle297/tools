"""Configuration management for report-bot"""

import json
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = {
    "team": {
        "name": "My Team",
        "members": [],
        "aliases": {},  # e.g., "john": "John Doe"
    },
    "defaults": {
        "author": None,
        "summarize": False,
        "format": "table",
    },
    "categorization": {
        "console_keywords": ["console", "ui", "frontend", "react"],
        "server_keywords": ["server", "backend", "api", "database"],
    },
    "tickets": {
        "patterns": [],  # Custom regex patterns for ticket extraction
    },
}


def get_config_path() -> Path:
    """Get path to config file

    Returns config file from (in order of priority):
    1. .report-bot.json in current directory
    2. ~/.config/report-bot/config.json
    3. ~/.report-bot.json
    """
    # Check current directory
    local_config = Path(".report-bot.json")
    if local_config.exists():
        return local_config

    # Check XDG config directory
    config_dir = Path.home() / ".config" / "report-bot"
    xdg_config = config_dir / "config.json"
    if xdg_config.exists():
        return xdg_config

    # Check home directory
    home_config = Path.home() / ".report-bot.json"
    if home_config.exists():
        return home_config

    # Return XDG config path as default (will be created if needed)
    return xdg_config


def load_config() -> dict[str, Any]:
    """Load configuration from file

    Returns:
        Configuration dictionary (or default config if file doesn't exist)
    """
    config_path = get_config_path()

    if not config_path.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(config_path, "r") as f:
            user_config = json.load(f)

        # Merge with defaults
        config = DEFAULT_CONFIG.copy()
        _deep_update(config, user_config)

        return config
    except Exception as e:
        print(f"Warning: Failed to load config from {config_path}: {e}")
        return DEFAULT_CONFIG.copy()


def _deep_update(base: dict, updates: dict) -> None:
    """Deep update base dictionary with updates"""
    for key, value in updates.items():
        if isinstance(value, dict) and key in base and isinstance(base[key], dict):
            _deep_update(base[key], value)
        else:
            base[key] = value


def save_config(config: dict[str, Any]) -> None:
    """Save configuration to file

    Args:
        config: Configuration dictionary to save
    """
    config_path = get_config_path()

    # Create directory if needed
    config_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        print(f"✓ Config saved to {config_path}")
    except Exception as e:
        print(f"Error: Failed to save config to {config_path}: {e}")


def init_config() -> None:
    """Initialize config file with defaults"""
    config_path = get_config_path()

    if config_path.exists():
        import sys

        try:
            response = input(f"Config file already exists at {config_path}. Overwrite? (y/N): ")
            if response.lower() != "y":
                print("Aborted.")
                return
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            return

    save_config(DEFAULT_CONFIG)
    print(f"\nConfig file created at: {config_path}")
    print("\nEdit this file to customize:")
    print("  - Team name and members")
    print("  - Default options")
    print("  - Component categorization keywords")
    print("  - Custom ticket patterns")


def get_team_members() -> list[str]:
    """Get team members from config

    Returns:
        List of team member names
    """
    config = load_config()
    return config.get("team", {}).get("members", [])


def get_author_alias(author: str) -> str:
    """Resolve author alias from config

    Args:
        author: Author name or alias

    Returns:
        Resolved author name (or original if no alias found)
    """
    config = load_config()
    aliases = config.get("team", {}).get("aliases", {})
    return aliases.get(author, author)


def get_default_options() -> dict[str, Any]:
    """Get default options from config

    Returns:
        Dictionary of default options
    """
    config = load_config()
    return config.get("defaults", {})
