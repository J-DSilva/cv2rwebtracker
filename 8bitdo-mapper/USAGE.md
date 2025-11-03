# 8bitdo Keyboard Mapper - Usage Guide

## Overview

This tool allows you to map the special A and B buttons on your 8bitdo retro keyboard (and any other keys) to custom actions on your Mac. You can configure keys to:

- Execute keyboard shortcuts (e.g., Command+Space)
- Launch applications
- Run shell commands
- Execute AppleScript
- Type text snippets

## Quick Start

1. **Start the application:**
   ```bash
   cd 8bitdo-mapper
   ./start.sh
   ```
   
   Or manually:
   ```bash
   python3 keyboard_mapper.py
   ```

2. **Open the web interface:**
   - Open your browser and go to `http://localhost:8080`

3. **Add your first mapping:**
   - Click "Add New Mapping"
   - Press the 8bitdo A or B button (or any key you want to map)
   - Select the action type
   - Enter the action command
   - Click "Save Mapping"

4. **Test it:**
   - Press your mapped key and watch the action execute!

## Finding 8bitdo A and B Key Codes

The 8bitdo retro keyboard's A and B buttons typically map to specific key codes on Mac. To find them:

1. Click "Add New Mapping" in the web interface
2. Press the A or B button on your 8bitdo keyboard
3. The captured key name will appear in the interface
4. Continue with configuring the action

Common 8bitdo key mappings:
- **A button**: Often maps to `KeyA` or a custom code
- **B button**: Often maps to `KeyB` or a custom code
- These may vary depending on your keyboard's firmware and mode

## Action Types

### 1. Keyboard Shortcut

Execute system or application keyboard shortcuts.

**Examples:**
- `Command+Space` - Open Spotlight
- `Command+Tab` - Switch applications
- `Control+Up` - Mission Control
- `Command+Shift+5` - Screenshot tool
- `Command+Option+Esc` - Force Quit dialog

**Format:**
- Use `Command`, `Control`, `Alt` (or `Option`), `Shift`
- Separate keys with `+`
- Case-insensitive

### 2. Shell Command

Run any terminal command or open applications.

**Examples:**
```bash
# Open applications
open -a "Safari"
open -a "Spotify"
open -a "Visual Studio Code"

# System controls
pmset displaysleepnow                    # Sleep displays
afplay /System/Library/Sounds/Glass.aiff # Play sound

# Volume control
osascript -e "set volume output volume 50"
osascript -e "set volume output volume (output volume of (get volume settings) + 10)"

# Open URLs
open "https://github.com"

# Run scripts
/path/to/your/script.sh
```

### 3. AppleScript

Execute AppleScript for advanced Mac automation.

**Examples:**
```applescript
# Show notification
display notification "Button pressed!" with title "8bitdo Mapper"

# Control iTunes/Music
tell application "Music" to playpause
tell application "Music" to next track

# Control system volume
set volume output volume 50

# Type text
tell application "System Events" to keystroke "Hello World"

# Get clipboard
set the clipboard to "Your text here"
```

### 4. Type Text

Automatically type text when key is pressed.

**Examples:**
- Email signatures
- Common phrases
- Code snippets
- Your email address
- Frequently used commands

## Example Configurations

### Gaming Setup
```json
{
  "KeyA": {
    "type": "shortcut",
    "action": "Command+H"
  },
  "KeyB": {
    "type": "command",
    "action": "open -a 'Discord'"
  }
}
```

### Productivity Setup
```json
{
  "KeyA": {
    "type": "shortcut",
    "action": "Command+Space"
  },
  "KeyB": {
    "type": "applescript",
    "action": "display notification \"Break time!\" with title \"Reminder\""
  }
}
```

### Media Control Setup
```json
{
  "KeyA": {
    "type": "applescript",
    "action": "tell application \"Music\" to playpause"
  },
  "KeyB": {
    "type": "applescript",
    "action": "tell application \"Music\" to next track"
  }
}
```

## Advanced Features

### Modifier Keys

You can capture key combinations that include modifier keys:
- Press Command, Control, Alt, or Shift along with the key
- The combination will be captured and displayed

### Testing Actions

Before saving a mapping:
1. Configure your action
2. Click "Test Action" to verify it works
3. Adjust if needed, then save

### Backing Up Configuration

Your mappings are stored in `config.json`. To backup:
```bash
cp config.json config.backup.json
```

To restore:
```bash
cp config.backup.json config.json
```

## Troubleshooting

### Keys Not Being Detected

1. **Check Accessibility Permissions:**
   - Go to System Preferences > Security & Privacy > Privacy > Accessibility
   - Ensure your terminal app (Terminal, iTerm2, etc.) is checked
   - If not listed, click the '+' button to add it

2. **Restart the Application:**
   ```bash
   # Stop with Ctrl+C, then restart
   ./start.sh
   ```

3. **Check Keyboard Connection:**
   - Ensure 8bitdo keyboard is properly connected
   - Try the buttons in another application to verify they work

### Actions Not Executing

1. **Test the Action:**
   - Use the "Test Action" button before saving
   - Try running the command in Terminal manually

2. **Check Syntax:**
   - For shortcuts: Use correct modifier names (Command, Control, etc.)
   - For commands: Verify the command works in Terminal
   - For AppleScript: Test in Script Editor first

3. **Check Permissions:**
   - Some actions may require additional permissions
   - Grant permissions in System Preferences > Security & Privacy

### Web Interface Not Loading

1. **Check if app is running:**
   ```bash
   # Should show the keyboard_mapper.py process
   ps aux | grep keyboard_mapper
   ```

2. **Check port availability:**
   ```bash
   # Port 8080 should be in use
   lsof -i :8080
   ```

3. **Try a different browser** or clear cache

### 8bitdo-Specific Issues

1. **Buttons Not Recognized:**
   - Try different connection modes (wired vs wireless)
   - Update 8bitdo keyboard firmware
   - Check keyboard's mode settings

2. **Buttons Send Wrong Keys:**
   - Some 8bitdo keyboards have multiple modes
   - Try switching modes with the mode button
   - Recapture keys in the configuration interface

## Running at Startup

### Option 1: LaunchAgent (Recommended)

Create a LaunchAgent plist file:

```bash
nano ~/Library/LaunchAgents/com.8bitdo.keyboardmapper.plist
```

Add:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.8bitdo.keyboardmapper</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/8bitdo-mapper/keyboard_mapper.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.8bitdo.keyboardmapper.plist
```

### Option 2: Login Items

1. Open System Preferences > Users & Groups
2. Click your user account
3. Click "Login Items" tab
4. Click '+' and add the start.sh script

## Uninstallation

1. Stop the application (Ctrl+C)
2. Remove LaunchAgent if configured:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.8bitdo.keyboardmapper.plist
   rm ~/Library/LaunchAgents/com.8bitdo.keyboardmapper.plist
   ```
3. Delete the 8bitdo-mapper directory

## Tips & Best Practices

1. **Start Simple:** Begin with basic shortcuts before complex commands
2. **Test First:** Always use "Test Action" before saving
3. **Backup Configs:** Keep a copy of your config.json
4. **Document Mappings:** Use clear, descriptive action values
5. **Don't Overwrite System Keys:** Avoid mapping critical system shortcuts
6. **Use Modifier Combinations:** Combine keys to avoid conflicts

## Getting Help

If you encounter issues:
1. Check the console output where keyboard_mapper.py is running
2. Review this usage guide
3. Check the main README.md
4. Open an issue on GitHub with:
   - Your macOS version
   - 8bitdo keyboard model
   - Error messages or logs
   - What you've tried

## License

MIT License - See LICENSE file for details
