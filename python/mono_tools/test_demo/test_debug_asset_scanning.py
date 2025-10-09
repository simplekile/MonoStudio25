#!/usr/bin/env python3
"""
Test script to verify debug output for asset scanning
"""

import os
import sys

def test_debug_asset_scanning():
    """Test that debug output is properly added for asset scanning"""
    print("Testing Debug Output for Asset Scanning...")
    print("=" * 60)
    
    # Check file_manager_helpers.py
    helpers_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'file_manager', 'file_manager_helpers.py')
    
    if not os.path.exists(helpers_file):
        print(f"X Helpers file not found: {helpers_file}")
        return False
    
    with open(helpers_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for debug prints in collect_asset_files
    debug_checks = [
        'collect_asset_files called with:',
        'Base directory does not exist:',
        'Assets directory does not exist:',
        'Assets directory found:',
        'Scanning asset types in:',
        'Found {len(type_entries)} entries in assets directory',
        'Checking entry: {type_entry.name}',
        'Processing asset type:',
        'Found {len(asset_entries)} asset entries',
        'Processing asset:',
        'Found {len(dept_entries)} department entries',
        'Processing department:',
        'Found {len(file_entries)} files in',
        'Found Houdini file:',
        'Skipping (not Houdini file):',
        'Final result: Found {len(results)} asset files',
        'HOUDINI_EXTS: {HOUDINI_EXTS}'
    ]
    
    print("\n=== DEBUG OUTPUT CHECKS ===")
    missing_debug = []
    for check in debug_checks:
        if check in content:
            print(f"OK Found debug: {check}")
        else:
            print(f"X Missing debug: {check}")
            missing_debug.append(check)
    
    # Summary
    total_issues = len(missing_debug)
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Missing debug output: {len(missing_debug)}")
    print(f"Total issues: {total_issues}")
    
    if total_issues == 0:
        print("\nSUCCESS: Debug output is properly added!")
        print("\nExpected debug output when scanning assets:")
        print("1. Function call parameters")
        print("2. Directory existence checks")
        print("3. Asset type scanning")
        print("4. Asset name scanning")
        print("5. Department scanning")
        print("6. File scanning with extension checks")
        print("7. Final results summary")
        return True
    else:
        print(f"\nFAILED: {total_issues} issues found.")
        return False

def main():
    """Main test function"""
    print("Debug Asset Scanning Test")
    print("=" * 60)
    
    success = test_debug_asset_scanning()
    
    print("\n" + "=" * 60)
    if success:
        print("Debug asset scanning test passed!")
        print("\nTo debug in Houdini:")
        print("1. Reload MiniBar in Houdini")
        print("2. Check Houdini console for detailed debug output")
        print("3. Look for specific error messages or missing directories")
        print("4. Verify file extensions and directory structure")
    else:
        print("Debug asset scanning test failed!")
    
    return success

if __name__ == "__main__":
    main()
