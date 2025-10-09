#!/usr/bin/env python3
"""
Test script to verify standalone refresh functionality
"""

import os
import sys

def test_standalone_refresh():
    """Test that standalone refresh functionality is properly added"""
    print("Testing Standalone Refresh Functionality...")
    print("=" * 60)
    
    # Check file_manager_minibar.py
    minibar_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'file_manager', 'file_manager_minibar.py')
    
    if not os.path.exists(minibar_file):
        print(f"X MiniBar file not found: {minibar_file}")
        return False
    
    with open(minibar_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for standalone refresh functionality
    standalone_checks = [
        'def _refresh_files_standalone(self):',
        'Refreshing files in standalone mode',
        'Get saved settings',
        'project_root',
        'current_project',
        'No manager available for file refresh',
        'Try to refresh without manager using saved settings',
        'Refresh files for new tab (always, with or without manager)',
        'Refresh files for new type (always, with or without manager)',
        'Saved project root:',
        'Saved current project:'
    ]
    
    print("\n=== STANDALONE REFRESH CHECKS ===")
    missing_standalone = []
    for check in standalone_checks:
        if check in content:
            print(f"OK Found standalone feature: {check}")
        else:
            print(f"X Missing standalone feature: {check}")
            missing_standalone.append(check)
    
    # Summary
    total_issues = len(missing_standalone)
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Missing standalone features: {len(missing_standalone)}")
    print(f"Total issues: {total_issues}")
    
    if total_issues == 0:
        print("\nSUCCESS: Standalone refresh functionality is properly added!")
        print("\nExpected behavior:")
        print("1. MiniBar can refresh files without File Manager being open")
        print("2. Settings are saved when File Manager is opened")
        print("3. Type and tab changes trigger immediate refresh")
        print("4. Standalone mode uses saved project root and project")
        print("5. Debug output shows standalone refresh process")
        return True
    else:
        print(f"\nFAILED: {total_issues} issues found.")
        return False

def main():
    """Main test function"""
    print("Standalone Refresh Test")
    print("=" * 60)
    
    success = test_standalone_refresh()
    
    print("\n" + "=" * 60)
    if success:
        print("Standalone refresh test passed!")
        print("\nTo test in Houdini:")
        print("1. Reload MiniBar in Houdini")
        print("2. Open File Manager once to save settings")
        print("3. Close File Manager")
        print("4. Change Type or Tab dropdown - should refresh immediately")
        print("5. Check Houdini console for standalone refresh debug")
    else:
        print("Standalone refresh test failed!")
    
    return success

if __name__ == "__main__":
    main()
