"""Clipboard monitoring and Zotero citation reformatting."""

import re
import threading
import time
from typing import Optional
import win32clipboard
from config import Config, OutputMode

# Enable debug logging
DEBUG = False


class ClipboardFormatter:
    """Handles clipboard monitoring and Zotero citation reformatting."""

    # Pattern to match Zotero citation format:
    # "content1" ([content2](content3)) ([content4](content5))
    # More flexible pattern that handles various spacing and quoting
    ZOTERO_PATTERN = re.compile(
        r'^"?([^"\n]+?)"?\s*\(\[.*?\]\(.*?\)\)\s*\(\[.*?\]\((.+?)\)\)$',
        re.DOTALL
    )

    # Pattern to strip surrounding quotes from title
    # Matches: "text", 'text', "text", 'text' (curly quotes)
    QUOTES_PATTERN = re.compile(r'^[\u0022\u0027\u201c\u2018](.+?)[\u0022\u0027\u201d\u2019]$')

    def __init__(self, config: Config):
        """Initialize the formatter with configuration.

        Args:
            config: Configuration instance for mode preference.
        """
        self.config = config
        self._last_clipboard_content = ""
        self._callbacks = []
        self._listening = False

    def add_callback(self, callback):
        """Register a callback function to be called after reformatting.

        Args:
            callback: Function to call with (original_text, reformatted_text).
        """
        self._callbacks.append(callback)

    def get_clipboard_text(self) -> Optional[str]:
        """Get current text content from clipboard.

        Returns:
            Clipboard text as string, or None if clipboard doesn't contain text.
        """
        try:
            win32clipboard.OpenClipboard()
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                    data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                    return data
            finally:
                win32clipboard.CloseClipboard()
        except Exception:
            pass
        return None

    def set_clipboard_text(self, text: str):
        """Set text content to clipboard.

        Args:
            text: Text to copy to clipboard.
        """
        try:
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, text)
            finally:
                win32clipboard.CloseClipboard()
        except Exception as e:
            print(f"Error setting clipboard: {e}")

    def matches_zotero_format(self, text: str) -> bool:
        """Check if text matches Zotero citation format.

        Args:
            text: Text to check.

        Returns:
            True if text matches Zotero format, False otherwise.
        """
        return bool(self.ZOTERO_PATTERN.match(text))

    def reformat(self, text: str) -> Optional[str]:
        """Reformat Zotero citation based on current mode.

        Args:
            text: Original text to reformat.

        Returns:
            Reformatted text, or None if text doesn't match Zotero format.
        """
        match = self.ZOTERO_PATTERN.match(text)
        if not match:
            return None

        title = match.group(1).strip()
        pdf_link = match.group(2).strip()

        # Strip surrounding quotes from title (both " and ' and ")
        title_match = self.QUOTES_PATTERN.match(title)
        if title_match:
            title = title_match.group(1)

        mode = self.config.get_mode()

        if mode == OutputMode.PLAIN_TEXT:
            return title
        elif mode == OutputMode.MARKDOWN_REFERENCE:
            return f"[{title}]({pdf_link})"

        return None

    def process_clipboard(self):
        """Process clipboard content and reformat if it's a Zotero citation."""
        current_text = self.get_clipboard_text()

        if DEBUG:
            print(f"Clipboard content: {repr(current_text[:100] if current_text else 'None')}...")

        if not current_text or current_text == self._last_clipboard_content:
            if DEBUG:
                print("Skipped: No new content")
            return

        self._last_clipboard_content = current_text

        # Check if it matches Zotero format
        matches = self.matches_zotero_format(current_text)
        if DEBUG:
            print(f"Matches Zotero format: {matches}")

        if matches:
            reformatted = self.reformat(current_text)
            if DEBUG and reformatted:
                print(f"Reformatted to: {repr(reformatted)}")

            if reformatted and reformatted != current_text:
                self.set_clipboard_text(reformatted)
                self._last_clipboard_content = reformatted
                if DEBUG:
                    print("Clipboard updated successfully!")

                # Notify callbacks
                for callback in self._callbacks:
                    try:
                        callback(current_text, reformatted)
                    except Exception as e:
                        print(f"Callback error: {e}")
