"""ZotClip - Zotero Citation Clipboard Reformatter.

A system tray application that automatically reformats Zotero citations
copied to clipboard into plain text or markdown reference format.
"""

import os
import sys
import threading
import time
from pathlib import Path

from PIL import Image
import pystray
from pynput import keyboard
import win32clipboard

from config import Config, OutputMode
from clipboard import ClipboardFormatter

# Enable debug logging
DEBUG = False


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller.

    Args:
        relative_path: Relative path to the resource file.

    Returns:
        Absolute path to the resource file.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        base_path = Path(__file__).parent

    return base_path / relative_path


class ZotClipApp:
    """Main application class managing system tray and clipboard monitoring."""

    def __init__(self):
        """Initialize the ZotClip application."""
        self.config = Config()
        self.formatter = ClipboardFormatter(self.config)
        self.icon = None
        self.running = False

        # Get icon path - works for both dev and PyInstaller
        self.icon_path = get_resource_path('icon.png')

        # Verify icon exists
        if not self.icon_path.exists():
            print(f"Warning: Icon file not found at {self.icon_path}")
            print("The application will run without a system tray icon.")
            self.icon_path = None

    def create_menu(self):
        """Create the system tray context menu.

        Returns:
            pystray.Menu object with all menu items.
        """
        def set_plain_text():
            """Set output mode to plain text."""
            self.config.set_mode(OutputMode.PLAIN_TEXT)
            self.update_menu()
            self.show_notification(f"Mode: {self.config.get_mode_display_name()}")

        def set_markdown_reference():
            """Set output mode to markdown reference."""
            self.config.set_mode(OutputMode.MARKDOWN_REFERENCE)
            self.update_menu()
            self.show_notification(f"Mode: {self.config.get_mode_display_name()}")

        def exit_app(icon):
            """Exit the application."""
            self.running = False
            icon.stop()

        # Create menu items
        plain_text_item = pystray.MenuItem(
            'Plain Text Mode',
            set_plain_text,
            checked=lambda item: self.config.get_mode() == OutputMode.PLAIN_TEXT
        )

        markdown_item = pystray.MenuItem(
            'Markdown Reference Mode',
            set_markdown_reference,
            checked=lambda item: self.config.get_mode() == OutputMode.MARKDOWN_REFERENCE
        )

        # Build menu
        menu = pystray.Menu(
            plain_text_item,
            markdown_item,
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Exit', exit_app)
        )

        return menu

    def update_menu(self):
        """Update the system tray menu after mode change."""
        if self.icon:
            self.icon.menu = self.create_menu()

    def show_notification(self, message: str, duration: int = 2):
        """Show a notification tooltip.

        Args:
            message: Message to display.
            duration: Duration in seconds (not supported on all platforms).
        """
        if self.icon:
            self.icon.notify(message, "ZotClip")

    def on_copy(self):
        """Handle Ctrl+C key press event."""
        if DEBUG:
            print("Ctrl+C detected!")

        # Wait for clipboard to update - use longer delay
        time.sleep(0.3)

        # Process clipboard in a separate thread to avoid blocking
        thread = threading.Thread(target=self.formatter.process_clipboard)
        thread.daemon = True
        thread.start()

    def setup_keyboard_listener(self):
        """Setup global keyboard listener for Ctrl+C detection."""
        # Track Ctrl key state
        ctrl_pressed = [False]

        def is_ctrl_key(key):
            """Check if key is a Ctrl key."""
            return key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.ctrl)

        def is_ctrl_c(key):
            """Check if key is Ctrl+C combination (comes as \\x03 control code)."""
            if hasattr(key, 'char'):
                # Ctrl+C comes through as the control code \x03
                return key.char == '\x03'
            return False

        def on_press(key):
            """Handle key press events."""
            try:
                if is_ctrl_key(key):
                    ctrl_pressed[0] = True
                    if DEBUG:
                        print("-> Ctrl pressed")
                elif is_ctrl_c(key):
                    # Ctrl+C detected!
                    if DEBUG:
                        print("-> Ctrl+C detected!")
                    self.on_copy()
            except AttributeError:
                if DEBUG:
                    print(f"AttributeError for key: {key}")

        def on_release(key):
            """Handle key release events."""
            try:
                if is_ctrl_key(key):
                    ctrl_pressed[0] = False
                    if DEBUG:
                        print("-> Ctrl released")
            except AttributeError:
                pass

        # Start listener in a separate thread
        listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        listener.start()

        return listener

    def run(self):
        """Run the main application."""
        # Check if icon is available
        if self.icon_path is None or not self.icon_path.exists():
            print("Error: Icon file not found. Cannot start application.")
            sys.exit(1)

        # Load icon image
        icon_image = Image.open(self.icon_path)

        # Create system tray icon
        self.icon = pystray.Icon(
            "zotclip",
            icon_image,
            "ZotClip - Zotero Citation Reformatter",
            menu=self.create_menu()
        )

        # Show initial mode
        current_mode = self.config.get_mode_display_name()
        print(f"ZotClip started - {current_mode}")

        # Setup keyboard listener
        listener = self.setup_keyboard_listener()

        # Set running flag
        self.running = True

        try:
            # Run the system tray icon
            self.icon.run()
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            listener.stop()


def main():
    """Entry point for the application."""
    app = ZotClipApp()
    app.run()


if __name__ == '__main__':
    main()
