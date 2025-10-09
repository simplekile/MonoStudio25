#!/usr/bin/env python3
"""
Test to verify the label attribute fix
"""

import os
import sys

def test_label_fix_verification():
    """Verify that the label attribute fix is in place"""
    print("Verifying label attribute fix...")
    
    # Check file_manager_manager.py
    manager_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'file_manager', 'file_manager_manager.py')
    
    if not os.path.exists(manager_file):
        print(f"X Manager file not found: {manager_file}")
        return False
    
    with open(manager_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for label attribute creation
    label_creation = [
        'self.asset_type_lbl = QtWidgets.QLabel("Asset Type")',
        'self.asset_name_lbl = QtWidgets.QLabel("Asset Name")',
        'self.department_lbl = QtWidgets.QLabel("Department")',
        'self.custom_dept_lbl = QtWidgets.QLabel("Custom Dept")'
    ]
    
    missing_creation = []
    for creation in label_creation:
        if creation in content:
            print(f"OK Found label creation: {creation}")
        else:
            print(f"X Missing label creation: {creation}")
            missing_creation.append(creation)
    
    # Check for safety checks in visibility method
    safety_checks = [
        'if hasattr(self, \'asset_type_lbl\') and self.asset_type_lbl:',
        'if hasattr(self, \'asset_name_lbl\') and self.asset_name_lbl:',
        'if hasattr(self, \'department_lbl\') and self.department_lbl:',
        'if hasattr(self, \'custom_dept_lbl\') and self.custom_dept_lbl:'
    ]
    
    missing_safety = []
    for check in safety_checks:
        if check in content:
            print(f"OK Found safety check: {check}")
        else:
            print(f"X Missing safety check: {check}")
            missing_safety.append(check)
    
    # Check for proper initialization order
    init_order_checks = [
        'self._init_asset_filtering()',
        'QHeaderView::section { background:#2a2a2a; color:#dcdcdc; border:0; padding:6px; }',
        '# Initialize asset filtering after UI is completely built'
    ]
    
    missing_order = []
    for check in init_order_checks:
        if check in content:
            print(f"OK Found init order: {check}")
        else:
            print(f"X Missing init order: {check}")
            missing_order.append(check)
    
    # Check that the old problematic direct access is removed
    problematic_access = [
        'self.asset_type_lbl.setVisible(is_assets)',
        'self.asset_name_lbl.setVisible(is_assets)',
        'self.department_lbl.setVisible(is_assets)',
        'self.custom_dept_lbl.setVisible(is_assets)'
    ]
    
    found_problematic = []
    for access in problematic_access:
        # These should NOT be found without safety checks
        if access in content and 'if hasattr(self,' not in content[content.find(access)-50:content.find(access)+50]:
            print(f"WARNING: Found unsafe direct access: {access}")
            found_problematic.append(access)
        else:
            print(f"OK Safe access pattern for: {access}")
    
    # Summary
    total_issues = len(missing_creation) + len(missing_safety) + len(missing_order) + len(found_problematic)
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Missing label creation: {len(missing_creation)}")
    print(f"Missing safety checks: {len(missing_safety)}")
    print(f"Missing init order: {len(missing_order)}")
    print(f"Unsafe direct access: {len(found_problematic)}")
    print(f"Total issues: {total_issues}")
    
    if total_issues == 0:
        print("\nSUCCESS: Label attribute fix is properly implemented!")
        print("The asset_type_lbl attribute error should be resolved.")
        return True
    else:
        print(f"\nFAILED: {total_issues} issues found.")
        return False

def main():
    """Main test function"""
    print("Verifying Label Attribute Fix...")
    print("=" * 60)
    
    success = test_label_fix_verification()
    
    print("\n" + "=" * 60)
    if success:
        print("Label attribute fix verification passed!")
    else:
        print("Label attribute fix verification failed!")
    
    return success

if __name__ == "__main__":
    main()
