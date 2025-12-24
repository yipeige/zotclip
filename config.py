"""Configuration management for ZotClip."""

import json
import os
from pathlib import Path
from enum import Enum


class OutputMode(Enum):
    """Output format modes."""
    PLAIN_TEXT = "plain_text"
    MARKDOWN_REFERENCE = "markdown_reference"


class Config:
    """Manages application configuration."""

    CONFIG_DIR = Path(os.getenv('APPDATA')) / 'zotclip'
    CONFIG_FILE = CONFIG_DIR / 'config.json'

    def __init__(self):
        """Initialize configuration, create default if not exists."""
        self._ensure_config_dir()
        self.config = self._load_config()

    def _ensure_config_dir(self):
        """Create configuration directory if it doesn't exist."""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> dict:
        """Load configuration from file or create default."""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # Return default configuration
        return {
            'mode': OutputMode.PLAIN_TEXT.value
        }

    def _save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save configuration: {e}")

    def get_mode(self) -> OutputMode:
        """Get current output mode."""
        mode_str = self.config.get('mode', OutputMode.PLAIN_TEXT.value)
        try:
            return OutputMode(mode_str)
        except ValueError:
            return OutputMode.PLAIN_TEXT

    def set_mode(self, mode: OutputMode):
        """Set output mode and persist to disk."""
        self.config['mode'] = mode.value
        self._save_config()

    def get_mode_display_name(self) -> str:
        """Get human-readable display name for current mode."""
        mode = self.get_mode()
        return {
            OutputMode.PLAIN_TEXT: "Plain Text Mode",
            OutputMode.MARKDOWN_REFERENCE: "Markdown Reference Mode"
        }[mode]
