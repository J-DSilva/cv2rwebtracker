# 8bitdo Retro Keyboard Mapper for Mac

A tool to enable full functionality of the 8bitdo retro keyboard on Mac computers, specifically allowing you to map the A and B keys (and other special keys) to any function you choose.

## Features

- Capture keyboard events from 8bitdo retro keyboard A and B buttons
- Map keys to custom actions, including:
  - Keyboard shortcuts
  - Application launches
  - Shell commands
  - AppleScript execution
- Web-based configuration interface
- Persistent configuration storage
- Real-time key event monitoring

## Requirements

- macOS 10.14 or later
- Python 3.7+
- pip (Python package manager)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/J-DSilva/cv2rwebtracker.git
   cd cv2rwebtracker/8bitdo-mapper
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Grant accessibility permissions to your terminal application in System Preferences > Security & Privacy > Privacy > Accessibility

## Usage

1. Start the keyboard mapper service:
   ```bash
   python3 keyboard_mapper.py
   ```

2. Open the configuration interface in your browser:
   ```
   http://localhost:8080
   ```

3. Configure your key mappings:
   - Click "Start Configuration"
   - Press the 8bitdo A or B button (or any other key)
   - Enter the action you want to map to that key
   - Save your configuration

4. The mapper will run in the background and execute your configured actions when you press the mapped keys

## Configuration File

Key mappings are stored in `config.json` in the following format:

```json
{
  "mappings": {
    "KeyA": {
      "type": "shortcut",
      "action": "Command+Space"
    },
    "KeyB": {
      "type": "command",
      "action": "open -a 'Safari'"
    }
  }
}
```

### Action Types

- **shortcut**: Execute keyboard shortcut (e.g., "Command+Space")
- **command**: Run shell command (e.g., "open -a 'Safari'")
- **applescript**: Execute AppleScript code
- **text**: Type text string

## Troubleshooting

### Keys not being detected
1. Ensure accessibility permissions are granted
2. Check that the 8bitdo keyboard is properly connected
3. Try running with `sudo` if permission issues persist

### Actions not executing
1. Verify your action syntax in the configuration
2. Test actions manually in terminal first
3. Check the application logs for errors

## Security Note

This application requires accessibility permissions to monitor keyboard events system-wide. It only processes keys that you explicitly configure and does not log or transmit any keyboard data.

## License

MIT License
