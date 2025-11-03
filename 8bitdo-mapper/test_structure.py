#!/usr/bin/env python3
"""
Test script for 8bitdo Keyboard Mapper
Validates code structure without requiring all dependencies
"""

import sys
import os
from pathlib import Path

def test_file_structure():
    """Test that all required files exist"""
    print("Testing file structure...")
    
    required_files = [
        'keyboard_mapper.py',
        'requirements.txt',
        'README.md',
        'USAGE.md',
        'config.example.json',
        'start.sh',
        'web/index.html',
        '.gitignore'
    ]
    
    base_path = Path(__file__).parent
    missing_files = []
    
    for file in required_files:
        file_path = base_path / file
        if not file_path.exists():
            missing_files.append(file)
            print(f"  ❌ Missing: {file}")
        else:
            print(f"  ✓ Found: {file}")
    
    if missing_files:
        print(f"\n❌ Test failed: {len(missing_files)} files missing")
        return False
    else:
        print("\n✓ All required files present")
        return True

def test_python_syntax():
    """Test that Python files have valid syntax"""
    print("\nTesting Python syntax...")
    
    import py_compile
    
    try:
        py_compile.compile('keyboard_mapper.py', doraise=True)
        print("  ✓ keyboard_mapper.py syntax is valid")
        return True
    except py_compile.PyCompileError as e:
        print(f"  ❌ Syntax error in keyboard_mapper.py: {e}")
        return False

def test_html_structure():
    """Test that HTML file has required elements"""
    print("\nTesting HTML structure...")
    
    with open('web/index.html', 'r') as f:
        html_content = f.read()
    
    required_elements = [
        '<title>8bitdo Keyboard Mapper</title>',
        'id="mapping-modal"',
        'id="mappings-container"',
        'function openAddModal()',
        'function saveMapping(',
        '/api/mappings',
    ]
    
    missing = []
    for element in required_elements:
        if element not in html_content:
            missing.append(element)
            print(f"  ❌ Missing: {element}")
        else:
            print(f"  ✓ Found: {element}")
    
    if missing:
        print(f"\n❌ Test failed: {len(missing)} elements missing")
        return False
    else:
        print("\n✓ All required HTML elements present")
        return True

def test_configuration_format():
    """Test that example config has correct format"""
    print("\nTesting configuration format...")
    
    import json
    
    try:
        with open('config.example.json', 'r') as f:
            config = json.load(f)
        
        if 'mappings' not in config:
            print("  ❌ Missing 'mappings' key")
            return False
        
        print("  ✓ Config has 'mappings' key")
        
        # Check that example mappings have required fields
        for key, mapping in config['mappings'].items():
            if 'type' not in mapping or 'action' not in mapping:
                print(f"  ❌ Mapping '{key}' missing required fields")
                return False
            print(f"  ✓ Mapping '{key}' is valid")
        
        print("\n✓ Configuration format is valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON: {e}")
        return False

def test_readme_content():
    """Test that README has key information"""
    print("\nTesting README content...")
    
    with open('README.md', 'r') as f:
        readme = f.read()
    
    required_sections = [
        '8bitdo',
        'Installation',
        'Usage',
        'Requirements',
        'Mac',
    ]
    
    missing = []
    for section in required_sections:
        if section not in readme:
            missing.append(section)
            print(f"  ❌ Missing section: {section}")
        else:
            print(f"  ✓ Found section: {section}")
    
    if missing:
        print(f"\n⚠️  Warning: {len(missing)} sections might be missing")
        return True  # Non-critical
    else:
        print("\n✓ README has key content")
        return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("8bitdo Keyboard Mapper - Validation Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Syntax", test_python_syntax),
        ("HTML Structure", test_html_structure),
        ("Configuration Format", test_configuration_format),
        ("README Content", test_readme_content),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
