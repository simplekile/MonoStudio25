#!/usr/bin/env python3
"""
Verify that the layout fix is in place
"""

import os
import sys

def test_layout_fix_verification():
    """Verify that the layout fix is in place"""
    print("Verifying layout fix...")
    
    # Check file_manager_manager.py
    manager_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'file_manager', 'file_manager_manager.py')
    
    if not os.path.exists(manager_file):
        print(f"X Manager file not found: {manager_file}")
        return False
    
    with open(manager_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for label attributes
    label_attrs = [
        'self.asset_type_lbl = QtWidgets.QLabel("Asset Type")',
        'self.asset_name_lbl = QtWidgets.QLabel("Asset Name")',
        'self.department_lbl = QtWidgets.QLabel("Department")',
        'self.custom_dept_lbl = QtWidgets.QLabel("Custom Dept")'
    ]
    
    missing_labels = []
    for attr in label_attrs:
        if attr in content:
            print(f"OK Found label: {attr}")
        else:
            print(f"X Missing label: {attr}")
            missing_labels.append(attr)
    
    # Check for the fixed visibility method
    visibility_fixes = [
        'self.asset_type_lbl.setVisible(is_assets)',
        'self.asset_name_lbl.setVisible(is_assets)',
        'self.department_lbl.setVisible(is_assets)',
        'self.custom_dept_lbl.setVisible(is_assets)'
    ]
    
    missing_visibility = []
    for fix in visibility_fixes:
        if fix in content:
            print(f"OK Found visibility fix: {fix}")
        else:
            print(f"X Missing visibility fix: {fix}")
            missing_visibility.append(fix)
    
    # Check that the old problematic code is removed
    problematic_code = [
        'item = layout.itemAtPosition(i, j)',
        'for i in range(2, 4):  # Rows 2 and 3',
        'for j in range(4):  # All columns'
    ]
    
    found_problematic = []
    for code in problematic_code:
        if code in content:
            print(f"WARNING: Found problematic code: {code}")
            found_problematic.append(code)
        else:
            print(f"OK Removed problematic code: {code}")
    
    # Summary
    total_issues = len(missing_labels) + len(missing_visibility) + len(found_problematic)
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Missing labels: {len(missing_labels)}")
    print(f"Missing visibility fixes: {len(missing_visibility)}")
    print(f"Problematic code still present: {len(found_problematic)}")
    print(f"Total issues: {total_issues}")
    
    if total_issues == 0:
        print("\nSUCCESS: Layout fix is properly implemented!")
        print("The itemAtPosition error should be resolved.")
        return True
    else:
        print(f"\nFAILED: {total_issues} issues found.")
        return False

def main():
    """Main test function"""
    print("Verifying Layout Fix...")
    print("=" * 60)
    
    success = test_layout_fix_verification()
    
    print("\n" + "=" * 60)
    if success:
        print("Layout fix verification passed!")
    else:
        print("Layout fix verification failed!")
    
    return success

if __name__ == "__main__":
    main()
