#!/usr/bin/env python3
"""
Test script to verify tab config for asset filtering
"""

import os
import sys

def test_tab_config():
    """Test that tab config has correct asset filtering values"""
    print("Testing Tab Config for Asset Filtering...")
    print("=" * 60)
    
    # Check file_manager_minibar.py
    minibar_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'file_manager', 'file_manager_minibar.py')
    
    if not os.path.exists(minibar_file):
        print(f"X MiniBar file not found: {minibar_file}")
        return False
    
    with open(minibar_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for asset tabs config
    asset_tabs_config = [
        '{"name": "models", "is_asset_tab": True, "asset_type": "_characters", "department": "01_modeling"}',
        '{"name": "rigging", "is_asset_tab": True, "asset_type": "_characters", "department": "02_rigging"}',
        '{"name": "surfacing", "is_asset_tab": True, "asset_type": "_characters", "department": "03_surfacing"}',
        '{"name": "lookdev", "is_asset_tab": True, "asset_type": "_characters", "department": "04_lookdev"}',
        '{"name": "groom", "is_asset_tab": True, "asset_type": "_characters", "department": "05_groom"}'
    ]
    
    print("\n=== ASSET TABS CONFIG ===")
    missing_config = []
    for config in asset_tabs_config:
        if config in content:
            print(f"OK Found tab config: {config}")
        else:
            print(f"X Missing tab config: {config}")
            missing_config.append(config)
    
    # Check for tab config usage in standalone mode
    standalone_checks = [
        'asset_type = tab_config.get(\'asset_type\')',
        'department = tab_config.get(\'department\')',
        'Only use UI controls if tab config doesn\'t have the values',
        'if not asset_type and hasattr(self, \'asset_type_cb\')',
        'if not department and hasattr(self, \'department_cb\')'
    ]
    
    print("\n=== STANDALONE MODE CHECKS ===")
    missing_standalone = []
    for check in standalone_checks:
        if check in content:
            print(f"OK Found standalone logic: {check}")
        else:
            print(f"X Missing standalone logic: {check}")
            missing_standalone.append(check)
    
    # Summary
    total_issues = len(missing_config) + len(missing_standalone)
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Missing tab config: {len(missing_config)}")
    print(f"Missing standalone logic: {len(missing_standalone)}")
    print(f"Total issues: {total_issues}")
    
    if total_issues == 0:
        print("\nSUCCESS: Tab config should work correctly!")
        print("\nExpected behavior:")
        print("1. Tab 'surfacing' should use asset_type='_characters', department='03_surfacing'")
        print("2. Tab 'lookdev' should use asset_type='_characters', department='04_lookdev'")
        print("3. Standalone mode should prioritize tab config over UI controls")
        print("4. Debug output should show correct filters from tab config")
        return True
    else:
        print(f"\nFAILED: {total_issues} issues found.")
        return False

def main():
    """Main test function"""
    print("Tab Config Test")
    print("=" * 60)
    
    success = test_tab_config()
    
    print("\n" + "=" * 60)
    if success:
        print("Tab config test passed!")
        print("\nTo test in Houdini:")
        print("1. Reload MiniBar in Houdini")
        print("2. Select 'surfacing' tab")
        print("3. Check debug output for correct filters")
        print("4. Should find files in 03_surfacing department")
    else:
        print("Tab config test failed!")
    
    return success

if __name__ == "__main__":
    main()
