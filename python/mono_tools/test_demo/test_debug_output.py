#!/usr/bin/env python3
"""
Test script to verify debug output in MiniBar
"""

import os
import sys

def test_debug_output():
    """Test that debug output is properly added"""
    print("Testing Debug Output in MiniBar...")
    print("=" * 50)
    
    # Check file_manager_minibar.py
    minibar_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'file_manager', 'file_manager_minibar.py')
    
    if not os.path.exists(minibar_file):
        print(f"X MiniBar file not found: {minibar_file}")
        return False
    
    with open(minibar_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for debug prints in populate method
    populate_debug_checks = [
        'Populating MiniBar with {len(paths)} files',
        'Files found:',
        'print(f"  {i+1}. {name} (v{ver or \'—\'})")',
        'No files found'
    ]
    
    print("\n=== POPULATE METHOD DEBUG ===")
    missing_populate = []
    for check in populate_debug_checks:
        if check in content:
            print(f"OK Found populate debug: {check}")
        else:
            print(f"X Missing populate debug: {check}")
            missing_populate.append(check)
    
    # Check for debug prints in _refresh_files_for_current_tab method
    refresh_debug_checks = [
        'Refreshing files for type {type_idx}',
        'Root: {root}',
        'Project: {project}',
        'Tab: {tab_config.get(\'name\', \'Unknown\')}',
        'Found {len(asset_files)} asset files',
        'Found {len(files)} shot files'
    ]
    
    print("\n=== REFRESH METHOD DEBUG ===")
    missing_refresh = []
    for check in refresh_debug_checks:
        if check in content:
            print(f"OK Found refresh debug: {check}")
        else:
            print(f"X Missing refresh debug: {check}")
            missing_refresh.append(check)
    
    # Check for debug prints in _on_tab_changed method
    tab_change_debug_checks = [
        'Tab changed to: {self.tab_cb.currentText()}',
        'Saved tab selection: {self.tab_cb.currentText()}'
    ]
    
    print("\n=== TAB CHANGE DEBUG ===")
    missing_tab_change = []
    for check in tab_change_debug_checks:
        if check in content:
            print(f"OK Found tab change debug: {check}")
        else:
            print(f"X Missing tab change debug: {check}")
            missing_tab_change.append(check)
    
    # Summary
    total_issues = len(missing_populate) + len(missing_refresh) + len(missing_tab_change)
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Missing populate debug: {len(missing_populate)}")
    print(f"Missing refresh debug: {len(missing_refresh)}")
    print(f"Missing tab change debug: {len(missing_tab_change)}")
    print(f"Total issues: {total_issues}")
    
    if total_issues == 0:
        print("\nSUCCESS: Debug output is properly added!")
        print("\nExpected debug output when using MiniBar:")
        print("1. When files are loaded:")
        print("   Populating MiniBar with X files")
        print("   Files found:")
        print("     1. filename.hip (v1)")
        print("     2. filename.hip (v2)")
        print("     ...")
        print("\n2. When tab changes:")
        print("   Tab changed to: models (index 0)")
        print("   Saved tab selection: models")
        print("   Refreshing files for type 0 (Assets)")
        print("   Root: /path/to/project")
        print("   Project: MyProject")
        print("   Tab: models")
        print("   Found X asset files")
        return True
    else:
        print(f"\nFAILED: {total_issues} issues found.")
        return False

def main():
    """Main test function"""
    print("Debug Output Test")
    print("=" * 50)
    
    success = test_debug_output()
    
    print("\n" + "=" * 50)
    if success:
        print("Debug output test passed!")
        print("\nTo see debug output in Houdini:")
        print("1. Reload MiniBar in Houdini")
        print("2. Change Type dropdown (Assets/Shots)")
        print("3. Change Tab dropdown")
        print("4. Check Houdini console for debug messages")
    else:
        print("Debug output test failed!")
    
    return success

if __name__ == "__main__":
    main()
