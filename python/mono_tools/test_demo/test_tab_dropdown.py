#!/usr/bin/env python3
"""
Test script to verify Tab Dropdown functionality
"""

import os
import sys

def test_tab_dropdown():
    """Test that Tab Dropdown shows correct items"""
    print("Testing Tab Dropdown Functionality...")
    
    # Check file_manager_minibar.py
    minibar_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'file_manager', 'file_manager_minibar.py')
    
    if not os.path.exists(minibar_file):
        print(f"X MiniBar file not found: {minibar_file}")
        return False
    
    with open(minibar_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for hardcoded configs
    assets_configs = [
        '"name": "models"',
        '"name": "rigging"',
        '"name": "surfacing"',
        '"name": "lookdev"',
        '"name": "groom"'
    ]
    
    shots_configs = [
        '"name": "lighting"',
        '"name": "animation"',
        '"name": "comp"'
    ]
    
    print("\n=== ASSETS CONFIG ===")
    missing_assets = []
    for config in assets_configs:
        if config in content:
            print(f"OK Found asset tab: {config}")
        else:
            print(f"X Missing asset tab: {config}")
            missing_assets.append(config)
    
    print("\n=== SHOTS CONFIG ===")
    missing_shots = []
    for config in shots_configs:
        if config in content:
            print(f"OK Found shot tab: {config}")
        else:
            print(f"X Missing shot tab: {config}")
            missing_shots.append(config)
    
    # Check for proper type handling
    type_checks = [
        'if type_index == 0:  # Assets',
        'if type_index == 0:  # Assets',
        'else:  # Shots',
        'self.tab_cb.setCurrentIndex(0)'
    ]
    
    print("\n=== TYPE HANDLING ===")
    missing_type = []
    for check in type_checks:
        if check in content:
            print(f"OK Found type handling: {check}")
        else:
            print(f"X Missing type handling: {check}")
            missing_type.append(check)
    
    # Summary
    total_issues = len(missing_assets) + len(missing_shots) + len(missing_type)
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Missing asset configs: {len(missing_assets)}")
    print(f"Missing shot configs: {len(missing_shots)}")
    print(f"Missing type handling: {len(missing_type)}")
    print(f"Total issues: {total_issues}")
    
    if total_issues == 0:
        print("\nSUCCESS: Tab Dropdown should work correctly!")
        print("Expected behavior:")
        print("- Assets mode: models, rigging, surfacing, lookdev, groom")
        print("- Shots mode: lighting, animation, comp")
        return True
    else:
        print(f"\nFAILED: {total_issues} issues found.")
        return False

def main():
    """Main test function"""
    print("Testing Tab Dropdown...")
    print("=" * 60)
    
    success = test_tab_dropdown()
    
    print("\n" + "=" * 60)
    if success:
        print("Tab Dropdown test passed!")
    else:
        print("Tab Dropdown test failed!")
    
    return success

if __name__ == "__main__":
    main()
