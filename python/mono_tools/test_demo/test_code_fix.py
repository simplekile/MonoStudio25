#!/usr/bin/env python3
"""
Test to verify File Manager fixes are in place by examining the code
"""

import os
import sys

def test_code_fixes():
    """Test that the code fixes are in place"""
    print("Testing File Manager code fixes...")
    
    # Check file_manager_manager.py
    manager_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'file_manager', 'file_manager_manager.py')
    
    if not os.path.exists(manager_file):
        print(f"X Manager file not found: {manager_file}")
        return False
    
    with open(manager_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required attributes
    required_attrs = [
        'self.status_label = QtWidgets.QLabel("Ready")',
        'self.custom_dept_le = QtWidgets.QLineEdit()',
        'self.asset_type_cb = QtWidgets.QComboBox()',
        'self.asset_name_cb = QtWidgets.QComboBox()',
        'self.department_cb = QtWidgets.QComboBox()',
        'self.type_tabs = QtWidgets.QTabWidget()',
        'self.assets_tab = QtWidgets.QWidget()',
        'self.shots_tab = QtWidgets.QWidget()'
    ]
    
    missing_attrs = []
    for attr in required_attrs:
        if attr in content:
            print(f"OK Found: {attr}")
        else:
            print(f"X Missing: {attr}")
            missing_attrs.append(attr)
    
    # Check for required methods
    required_methods = [
        'def _init_asset_filtering(self):',
        'def _reload_asset_types(self):',
        'def _reload_asset_names(self):',
        'def _reload_departments(self):',
        'def _update_asset_filter_visibility(self):',
        'def _on_asset_type_changed(self, text):',
        'def _on_asset_name_changed(self, text):',
        'def _on_department_changed(self, text):',
        'def _on_custom_department_changed(self, text):'
    ]
    
    missing_methods = []
    for method in required_methods:
        if method in content:
            print(f"OK Found: {method}")
        else:
            print(f"X Missing: {method}")
            missing_methods.append(method)
    
    # Check for error handling fixes
    error_handling_fixes = [
        'if hasattr(self, \'status_label\') and self.status_label:',
        'if hasattr(self, \'custom_dept_le\') and self.custom_dept_le:',
        'if hasattr(self, \'type_tabs\') and self.type_tabs.currentIndex() == 0:',
        'layout = self.layout()\n        if layout:'
    ]
    
    missing_error_handling = []
    for fix in error_handling_fixes:
        if fix in content:
            print(f"OK Found error handling: {fix[:50]}...")
        else:
            print(f"X Missing error handling: {fix[:50]}...")
            missing_error_handling.append(fix)
    
    # Check for asset scanning logic
    asset_scanning_fixes = [
        'if self.type_tabs.currentIndex() == 0:  # Assets tab',
        'collect_asset_files(',
        'AssetTableModel',
        'asset_type = self.asset_type_cb.currentText()',
        'asset_name = self.asset_name_cb.currentText()',
        'department = self.department_cb.currentText()'
    ]
    
    missing_asset_scanning = []
    for fix in asset_scanning_fixes:
        if fix in content:
            print(f"OK Found asset scanning: {fix}")
        else:
            print(f"X Missing asset scanning: {fix}")
            missing_asset_scanning.append(fix)
    
    # Check file_manager_helpers.py
    helpers_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'file_manager', 'file_manager_helpers.py')
    
    if not os.path.exists(helpers_file):
        print(f"X Helpers file not found: {helpers_file}")
        return False
    
    with open(helpers_file, 'r', encoding='utf-8') as f:
        helpers_content = f.read()
    
    # Check for asset helper functions
    asset_helpers = [
        'def collect_asset_files(base_dir, asset_type=None, department=None):',
        'def list_asset_types(base_dir):',
        'def list_asset_names(base_dir, asset_type):',
        'def list_departments(base_dir, asset_type, asset_name):',
        'def infer_asset_name(full_path):',
        'def infer_department(full_path):'
    ]
    
    missing_helpers = []
    for helper in asset_helpers:
        if helper in helpers_content:
            print(f"OK Found helper: {helper}")
        else:
            print(f"X Missing helper: {helper}")
            missing_helpers.append(helper)
    
    # Check file_manager_models.py
    models_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'file_manager', 'file_manager_models.py')
    
    if not os.path.exists(models_file):
        print(f"X Models file not found: {models_file}")
        return False
    
    with open(models_file, 'r', encoding='utf-8') as f:
        models_content = f.read()
    
    # Check for AssetTableModel
    asset_model_checks = [
        'class AssetTableModel(QtGui.QStandardItemModel):',
        'COL_ASSET=0; COL_DEPT=1; COL_VER=2; COL_NAME=3; COL_EXT=4; COL_FOLDER=5; COL_MOD=6; COL_SIZE=7',
        'HEAD=["Asset Name","Department","Ver","File Name","Ext","Folder","Modified","Size"]'
    ]
    
    missing_models = []
    for check in asset_model_checks:
        if check in models_content:
            print(f"OK Found model: {check}")
        else:
            print(f"X Missing model: {check}")
            missing_models.append(check)
    
    # Summary
    total_issues = len(missing_attrs) + len(missing_methods) + len(missing_error_handling) + len(missing_asset_scanning) + len(missing_helpers) + len(missing_models)
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Missing attributes: {len(missing_attrs)}")
    print(f"Missing methods: {len(missing_methods)}")
    print(f"Missing error handling: {len(missing_error_handling)}")
    print(f"Missing asset scanning: {len(missing_asset_scanning)}")
    print(f"Missing helpers: {len(missing_helpers)}")
    print(f"Missing models: {len(missing_models)}")
    print(f"Total issues: {total_issues}")
    
    if total_issues == 0:
        print("\nSUCCESS: All fixes are in place! The Asset Finder should work without attribute errors.")
        return True
    else:
        print(f"\nFAILED: {total_issues} issues found. Please check the missing items above.")
        return False

def main():
    """Main test function"""
    print("Testing File Manager Code Fixes...")
    print("=" * 60)
    
    success = test_code_fixes()
    
    print("\n" + "=" * 60)
    if success:
        print("All code fixes are in place!")
        print("The Asset Finder should now work without attribute errors.")
    else:
        print("Some fixes are missing. Please check the issues above.")
    
    return success

if __name__ == "__main__":
    main()
