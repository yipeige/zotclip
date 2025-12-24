# ZotClip

A Windows system tray application that automatically reformats Zotero citations copied to clipboard.

## Features

- **Automatic Reformatting**: Detects and reformats Zotero citations when copied (Ctrl+C)
- **Two Output Modes**:
  - **Plain Text Mode**: Extracts only the title (quotes removed)
  - **Markdown Reference Mode**: Creates `[title](pdf-link)` format
- **System Tray Integration**: Runs in background with easy mode switching
- **Resource Efficient**: Only activates on Ctrl+C, no continuous polling
- **Quote Handling**: Automatically strips all quote types (`, ", ', ')

## Installation

### From EXE (Recommended)

Simply run `ZotClip.exe` - no installation required.

### From Source

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Usage

1. **Start the Application**: Double-click `ZotClip.exe`
2. **Select Mode**: Right-click the system tray icon to choose:
   - Plain Text Mode
   - Markdown Reference Mode
3. **Copy from Zotero**: Copy any Zotero citation as usual (Ctrl+C)
4. **Auto-Reformat**: Paste the reformatted citation anywhere

### Example

**Original (from Zotero):**
```
"loss-free balance routing" ([Team et al., 2025, p. 2](zotero://select/library/items/UVG6GBGT)) ([pdf](zotero://open-pdf/library/items/NUG9I57I?page=2&annotation=FIFCZW5L))
```

**Plain Text Mode:**
```
loss-free balance routing
```

**Markdown Reference Mode:**
```
[loss-free balance routing](zotero://open-pdf/library/items/NUG9I57I?page=2&annotation=FIFCZW5L)
```

## Building EXE

```bash
# Install PyInstaller
pip install pyinstaller

# Build using spec file (recommended)
pyinstaller build.spec

# Or build manually
pyinstaller --onefile --windowed --icon=icon.png --add-data "icon.png;." main.py
```

The compiled EXE will be in the `dist/` folder.

### Building with Console (Debug Mode)

If you need to see debug output:
```bash
pyinstaller --onefile --console --icon=icon.png --add-data "icon.png;." main.py
```

Then set `DEBUG = True` in `main.py` and `clipboard.py`.

## Configuration

User preferences are stored in:
```
%APPDATA%\zotclip\config.json
```

## Requirements

- Windows 10/11
- Python 3.8+ (for development)
- Zotero (for generating source citations)

## Project Structure

```
zotclip/
├── main.py           # Entry point, system tray, keyboard hook
├── clipboard.py      # Clipboard monitoring and reformatting
├── config.py         # Configuration management
├── icon.png          # System tray icon
├── requirements.txt  # Python dependencies
├── build.spec        # PyInstaller spec file
├── test_pattern.py   # Test script for regex pattern
└── README.md         # This file
```

## How It Works

1. **Keyboard Hook**: Uses `pynput` to detect Ctrl+C key combinations globally
2. **Clipboard Monitoring**: After Ctrl+C is detected, reads clipboard content
3. **Pattern Matching**: Uses regex to detect Zotero citation format
4. **Reformatting**: Transforms citation based on selected mode
5. **Clipboard Update**: Writes reformatted text back to clipboard

## Troubleshooting

**EXE doesn't start / no icon in system tray:**
- Rebuild with `--console` flag to see error messages
- Ensure `icon.png` exists in the same directory as the script

**Citation not being reformatted:**
- Verify the Zotero citation format matches the expected pattern
- Run `test_pattern.py` to test regex matching

**Mode changes not persisting:**
- Check write permissions for `%APPDATA%\zotclip\`

## License

MIT License
