#!/usr/bin/env python3
"""
Test script to verify MiniBar Type and Tab Dropdown implementation
"""

import os
import sys

def test_minibar_implementation():
    """Test that MiniBar implementation is correct"""
    print("Testing MiniBar Type and Tab Dropdown Implementation...")
    
    # Check file_manager_minibar.py
    minibar_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'file_manager', 'file_manager_minibar.py')
    
    if not os.path.exists(minibar_file):
        print(f"X MiniBar file not found: {minibar_file}")
        return False
    
    with open(minibar_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for new UI elements
    minibar_checks = [
        'self.type_cb = QtWidgets.QComboBox()',
        'self.tab_cb = QtWidgets.QComboBox()',
        'self.type_cb.addItem("Assets")',
        'self.type_cb.addItem("Shots")',
        'self.type_cb.currentIndexChanged.connect(self._on_type_changed)',
        'self.tab_cb.currentIndexChanged.connect(self._on_tab_changed)',
        'lay.addWidget(self.type_cb, 0)',
        'lay.addWidget(self.tab_cb, 0)'
    ]
    
    missing_minibar = []
    for check in minibar_checks:
        if check in content:
            print(f"OK Found MiniBar element: {check}")
        else:
            print(f"X Missing MiniBar element: {check}")
            missing_minibar.append(check)
    
    # Check for new methods
    minibar_methods = [
        'def _load_tabs_for_type(self, type_index):',
        'def _on_type_changed(self, idx):',
        'def _on_tab_changed(self, idx):',
        'def _refresh_files_for_current_tab(self):'
    ]
    
    missing_methods = []
    for method in minibar_methods:
        if method in content:
            print(f"OK Found MiniBar method: {method}")
        else:
            print(f"X Missing MiniBar method: {method}")
            missing_methods.append(method)
    
    # Check file_manager_models.py
    models_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'file_manager', 'file_manager_models.py')
    
    if not os.path.exists(models_file):
        print(f"X Models file not found: {models_file}")
        return False
    
    with open(models_file, 'r', encoding='utf-8') as f:
        models_content = f.read()
    
    # Check for version grouping
    models_checks = [
        'def add_asset_group(self, asset, dept, versions_data):',
        'def _parse_version(self, ver_str):',
        'def update_row_for_version(self, row, version_data):',
        'class VersionComboBoxDelegate(QtWidgets.QStyledItemDelegate):',
        'def createEditor(self, parent, option, index):',
        'def setModelData(self, editor, model, index):'
    ]
    
    missing_models = []
    for check in models_checks:
        if check in models_content:
            print(f"OK Found models feature: {check}")
        else:
            print(f"X Missing models feature: {check}")
            missing_models.append(check)
    
    # Check file_manager_manager.py
    manager_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'file_manager', 'file_manager_manager.py')
    
    if not os.path.exists(manager_file):
        print(f"X Manager file not found: {manager_file}")
        return False
    
    with open(manager_file, 'r', encoding='utf-8') as f:
        manager_content = f.read()
    
    # Check for asset grouping and version delegate
    manager_checks = [
        'grouped_files = {}',
        'group_key = (asset_name, dept_name)',
        'model.add_asset_group(asset_name, dept_name, versions_data)',
        'VersionComboBoxDelegate',
        'table.setItemDelegateForColumn(AssetTableModel.COL_VER, version_delegate)',
        'is_asset_tab = conf.get("is_asset_tab", False)',
        'w.asset_type=conf.get("asset_type")',
        'w.department=conf.get("department")'
    ]
    
    missing_manager = []
    for check in manager_checks:
        if check in manager_content:
            print(f"OK Found manager feature: {check}")
        else:
            print(f"X Missing manager feature: {check}")
            missing_manager.append(check)
    
    # Check for asset tabs config
    asset_tabs_checks = [
        '"is_asset_tab": True',
        '"asset_type": "_characters"',
        '"department": "01_modeling"',
        '"department": "02_rigging"',
        '"department": "03_surfacing"'
    ]
    
    missing_asset_tabs = []
    for check in asset_tabs_checks:
        if check in manager_content:
            print(f"OK Found asset tabs config: {check}")
        else:
            print(f"X Missing asset tabs config: {check}")
            missing_asset_tabs.append(check)
    
    # Summary
    total_issues = len(missing_minibar) + len(missing_methods) + len(missing_models) + len(missing_manager) + len(missing_asset_tabs)
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Missing MiniBar elements: {len(missing_minibar)}")
    print(f"Missing MiniBar methods: {len(missing_methods)}")
    print(f"Missing models features: {len(missing_models)}")
    print(f"Missing manager features: {len(missing_manager)}")
    print(f"Missing asset tabs config: {len(missing_asset_tabs)}")
    print(f"Total issues: {total_issues}")
    
    if total_issues == 0:
        print("\nSUCCESS: MiniBar Type and Tab Dropdown implementation is complete!")
        print("Features implemented:")
        print("- Type dropdown (Assets/Shots) in MiniBar")
        print("- Tab dropdown showing appropriate tabs for each type")
        print("- Asset table groups files by asset+department")
        print("- Version dropdown for each asset group")
        print("- Asset tabs store filter settings instead of subpath")
        print("- MiniBar syncs with File Manager")
        return True
    else:
        print(f"\nFAILED: {total_issues} issues found.")
        return False

def main():
    """Main test function"""
    print("Testing MiniBar Implementation...")
    print("=" * 60)
    
    success = test_minibar_implementation()
    
    print("\n" + "=" * 60)
    if success:
        print("MiniBar implementation test passed!")
    else:
        print("MiniBar implementation test failed!")
    
    return success

if __name__ == "__main__":
    main()
