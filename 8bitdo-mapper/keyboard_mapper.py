#!/usr/bin/env python3
"""
8bitdo Keyboard Mapper for Mac
Captures keyboard events and executes configured actions
"""

import json
import os
import subprocess
import threading
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pynput import keyboard
from pynput.keyboard import Controller, Key

# Configuration
CONFIG_FILE = Path(__file__).parent / "config.json"
WEB_DIR = Path(__file__).parent / "web"

# Global state
current_mappings = {}
keyboard_controller = Controller()
active_listener = None

app = Flask(__name__, static_folder='web')
CORS(app)


def load_config():
    """Load key mappings from config file"""
    global current_mappings
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                current_mappings = config.get('mappings', {})
                print(f"Loaded {len(current_mappings)} key mappings")
        except Exception as e:
            print(f"Error loading config: {e}")
            current_mappings = {}
    else:
        current_mappings = {}
        save_config()


def save_config():
    """Save key mappings to config file"""
    try:
        config = {'mappings': current_mappings}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print("Configuration saved")
    except Exception as e:
        print(f"Error saving config: {e}")


def get_key_name(key):
    """Convert pynput key to string identifier"""
    try:
        if hasattr(key, 'char') and key.char:
            return f"Key{key.char.upper()}"
        elif hasattr(key, 'name'):
            return key.name.capitalize()
        else:
            return str(key)
    except AttributeError:
        return str(key)


def execute_action(action_config):
    """Execute the configured action"""
    action_type = action_config.get('type', 'command')
    action = action_config.get('action', '')
    
    print(f"Executing {action_type}: {action}")
    
    try:
        if action_type == 'command':
            # Execute shell command
            subprocess.Popen(action, shell=True)
            
        elif action_type == 'shortcut':
            # Execute keyboard shortcut
            execute_shortcut(action)
            
        elif action_type == 'applescript':
            # Execute AppleScript
            subprocess.Popen(['osascript', '-e', action])
            
        elif action_type == 'text':
            # Type text
            keyboard_controller.type(action)
            
    except Exception as e:
        print(f"Error executing action: {e}")


def execute_shortcut(shortcut):
    """Execute a keyboard shortcut like 'Command+Space'"""
    parts = shortcut.split('+')
    keys = []
    
    # Map common key names to pynput keys
    key_map = {
        'command': Key.cmd,
        'cmd': Key.cmd,
        'control': Key.ctrl,
        'ctrl': Key.ctrl,
        'alt': Key.alt,
        'option': Key.alt,
        'shift': Key.shift,
        'space': Key.space,
        'enter': Key.enter,
        'return': Key.enter,
        'tab': Key.tab,
        'escape': Key.esc,
        'esc': Key.esc,
    }
    
    for part in parts:
        part_lower = part.strip().lower()
        if part_lower in key_map:
            keys.append(key_map[part_lower])
        elif len(part.strip()) == 1:
            keys.append(part.strip().lower())
    
    # Press all keys
    for key in keys:
        keyboard_controller.press(key)
    
    # Release in reverse order
    for key in reversed(keys):
        keyboard_controller.release(key)


def on_key_press(key):
    """Handle key press events"""
    key_name = get_key_name(key)
    
    # Check if this key has a mapping
    if key_name in current_mappings:
        print(f"Key {key_name} pressed - executing mapped action")
        # Execute the action in a separate thread to avoid blocking
        action_config = current_mappings[key_name]
        threading.Thread(target=execute_action, args=(action_config,), daemon=True).start()
        # Return False to suppress the key (optional - can be made configurable)
        # For now, let the key through so it still works normally
        return True


def start_keyboard_listener():
    """Start listening for keyboard events"""
    global active_listener
    
    if active_listener:
        active_listener.stop()
    
    active_listener = keyboard.Listener(on_press=on_key_press)
    active_listener.start()
    print("Keyboard listener started")


# Flask routes

@app.route('/')
def index():
    """Serve the web interface"""
    return send_from_directory(WEB_DIR, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory(WEB_DIR, path)


@app.route('/api/mappings', methods=['GET'])
def get_mappings():
    """Get current key mappings"""
    return jsonify({'mappings': current_mappings})


@app.route('/api/mappings', methods=['POST'])
def set_mappings():
    """Update key mappings"""
    global current_mappings
    try:
        data = request.json
        current_mappings = data.get('mappings', {})
        save_config()
        return jsonify({'success': True, 'mappings': current_mappings})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/mapping', methods=['POST'])
def add_mapping():
    """Add or update a single key mapping"""
    try:
        data = request.json
        key_name = data.get('key')
        action_config = {
            'type': data.get('type', 'command'),
            'action': data.get('action', '')
        }
        
        current_mappings[key_name] = action_config
        save_config()
        return jsonify({'success': True, 'key': key_name, 'config': action_config})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/mapping/<key_name>', methods=['DELETE'])
def delete_mapping(key_name):
    """Delete a key mapping"""
    try:
        if key_name in current_mappings:
            del current_mappings[key_name]
            save_config()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/test', methods=['POST'])
def test_action():
    """Test an action without saving it"""
    try:
        data = request.json
        action_config = {
            'type': data.get('type', 'command'),
            'action': data.get('action', '')
        }
        execute_action(action_config)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


def main():
    """Main entry point"""
    print("8bitdo Keyboard Mapper for Mac")
    print("=" * 40)
    
    # Load configuration
    load_config()
    
    # Start keyboard listener
    start_keyboard_listener()
    
    # Start web server
    print(f"\nWeb interface available at: http://localhost:8080")
    print("Press Ctrl+C to stop\n")
    
    try:
        app.run(host='0.0.0.0', port=8080, debug=False)
    except KeyboardInterrupt:
        print("\nStopping keyboard mapper...")
        if active_listener:
            active_listener.stop()


if __name__ == '__main__':
    main()
