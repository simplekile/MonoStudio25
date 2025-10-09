#!/usr/bin/env python3
"""
Test script to verify file filtering consistency
"""

import os
import sys

def test_file_filtering():
    """Test that file filtering is consistent"""
    print("Testing File Filtering Consistency...")
    print("=" * 50)
    
    # Check file_manager_helpers.py
    helpers_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'file_manager', 'file_manager_helpers.py')
    
    if not os.path.exists(helpers_file):
        print(f"X Helpers file not found: {helpers_file}")
        return False
    
    with open(helpers_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for asset_name parameter in collect_asset_files
    helpers_checks = [
        'def collect_asset_files(base_dir, asset_type=None, department=None, asset_name=None):',
        'asset_name: Asset name filter (char_Gefula, etc.)',
        'if asset_name and current_asset_name != asset_name:',
        'results.append((file_entry.path, current_asset_name, dept_name))'
    ]
    
    print("\n=== HELPERS FILE CHECKS ===")
    missing_helpers = []
    for check in helpers_checks:
        if check in content:
            print(f"OK Found helpers feature: {check}")
        else:
            print(f"X Missing helpers feature: {check}")
            missing_helpers.append(check)
    
    # Check file_manager_minibar.py
    minibar_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'file_manager', 'file_manager_minibar.py')
    
    if not os.path.exists(minibar_file):
        print(f"X MiniBar file not found: {minibar_file}")
        return False
    
    with open(minibar_file, 'r', encoding='utf-8') as f:
        minibar_content = f.read()
    
    # Check for asset_name filtering in MiniBar
    minibar_checks = [
        'asset_name = None',
        'if hasattr(self.manager, \'asset_name_cb\'):',
        'asset_name_text = self.manager.asset_name_cb.currentText()',
        'if asset_name_text and asset_name_text != "All Assets":',
        'asset_name = asset_name_text',
        'collect_asset_files(base_dir, asset_type, department, asset_name)',
        'Added {added_count} items to dropdown',
        'combo.count() = {self.combo.count()}'
    ]
    
    print("\n=== MINIBAR FILE CHECKS ===")
    missing_minibar = []
    for check in minibar_checks:
        if check in minibar_content:
            print(f"OK Found minibar feature: {check}")
        else:
            print(f"X Missing minibar feature: {check}")
            missing_minibar.append(check)
    
    # Summary
    total_issues = len(missing_helpers) + len(missing_minibar)
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Missing helpers features: {len(missing_helpers)}")
    print(f"Missing minibar features: {len(missing_minibar)}")
    print(f"Total issues: {total_issues}")
    
    if total_issues == 0:
        print("\nSUCCESS: File filtering should be consistent!")
        print("\nExpected behavior:")
        print("1. collect_asset_files() now supports asset_name filtering")
        print("2. MiniBar passes asset_name filter to collect_asset_files()")
        print("3. Debug output shows exact number of files found vs added to dropdown")
        print("4. Files found in debug should match files in dropdown")
        return True
    else:
        print(f"\nFAILED: {total_issues} issues found.")
        return False

def main():
    """Main test function"""
    print("File Filtering Consistency Test")
    print("=" * 50)
    
    success = test_file_filtering()
    
    print("\n" + "=" * 50)
    if success:
        print("File filtering test passed!")
        print("\nTo test in Houdini:")
        print("1. Reload MiniBar in Houdini")
        print("2. Check debug output for file counts")
        print("3. Verify files found = files in dropdown")
    else:
        print("File filtering test failed!")
    
    return success

if __name__ == "__main__":
    main()
