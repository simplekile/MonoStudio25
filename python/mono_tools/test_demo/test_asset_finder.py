#!/usr/bin/env python3
"""
Test script for Asset Finder functionality
Tests the new asset scanning and filtering features in File Manager
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def create_test_asset_structure(base_dir):
    """Create a test asset structure for testing"""
    print("Creating test asset structure...")
    
    # Create 01_assets directory structure
    assets_dir = os.path.join(base_dir, "01_assets")
    
    # Create asset types
    asset_types = ["_characters", "_environments", "_graphic"]
    
    for asset_type in asset_types:
        type_dir = os.path.join(assets_dir, asset_type)
        os.makedirs(type_dir, exist_ok=True)
        
        if asset_type == "_characters":
            # Create character assets
            characters = ["char_Gefula", "char_Hero", "char_Villain"]
            for char in characters:
                char_dir = os.path.join(type_dir, char)
                os.makedirs(char_dir, exist_ok=True)
                
                # Create departments
                departments = ["01_modeling", "02_rigging", "03_surfacing", "04_lookdev", "05_groom"]
                for dept in departments:
                    dept_dir = os.path.join(char_dir, dept)
                    os.makedirs(dept_dir, exist_ok=True)
                    
                    # Create sample .hip files
                    for i in range(1, 4):  # 3 versions each
                        filename = f"{char}_{dept}_v{i:03d}.hip"
                        filepath = os.path.join(dept_dir, filename)
                        with open(filepath, 'w') as f:
                            f.write(f"# Test Houdini file: {filename}\n")
                            f.write(f"# Created: {datetime.now()}\n")
        
        elif asset_type == "_environments":
            # Create environment assets
            environments = ["env_Forest", "env_City", "env_Desert"]
            for env in environments:
                env_dir = os.path.join(type_dir, env)
                os.makedirs(env_dir, exist_ok=True)
                
                # Create departments
                departments = ["01_modeling", "04_lookdev", "05_lighting"]
                for dept in departments:
                    dept_dir = os.path.join(env_dir, dept)
                    os.makedirs(dept_dir, exist_ok=True)
                    
                    # Create sample .hip files
                    for i in range(1, 3):  # 2 versions each
                        filename = f"{env}_{dept}_v{i:03d}.hip"
                        filepath = os.path.join(dept_dir, filename)
                        with open(filepath, 'w') as f:
                            f.write(f"# Test Houdini file: {filename}\n")
                            f.write(f"# Created: {datetime.now()}\n")
        
        elif asset_type == "_graphic":
            # Create graphic assets
            graphics = ["graphic_Logo", "graphic_UI"]
            for graphic in graphics:
                graphic_dir = os.path.join(type_dir, graphic)
                os.makedirs(graphic_dir, exist_ok=True)
                
                # Create departments
                departments = ["01_design", "02_animation"]
                for dept in departments:
                    dept_dir = os.path.join(graphic_dir, dept)
                    os.makedirs(dept_dir, exist_ok=True)
                    
                    # Create sample .hip files
                    for i in range(1, 2):  # 1 version each
                        filename = f"{graphic}_{dept}_v{i:03d}.hip"
                        filepath = os.path.join(dept_dir, filename)
                        with open(filepath, 'w') as f:
                            f.write(f"# Test Houdini file: {filename}\n")
                            f.write(f"# Created: {datetime.now()}\n")
    
    print(f"Test structure created at: {assets_dir}")
    return assets_dir

def test_asset_helpers():
    """Test the asset helper functions"""
    print("\nTesting asset helper functions...")
    
    try:
        from mono_tools.file_manager.file_manager_helpers import (
            collect_asset_files, list_asset_types, list_asset_names, 
            list_departments, infer_asset_name, infer_department
        )
        
        # Create temporary test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test structure
            assets_dir = create_test_asset_structure(temp_dir)
            
            # Test list_asset_types
            print("Testing list_asset_types...")
            types = list_asset_types(temp_dir)
            print(f"   Found types: {types}")
            assert "_characters" in types
            assert "_environments" in types
            assert "_graphic" in types
            
            # Test list_asset_names
            print("Testing list_asset_names...")
            char_names = list_asset_names(temp_dir, "_characters")
            print(f"   Character assets: {char_names}")
            assert "char_Gefula" in char_names
            
            # Test list_departments
            print("Testing list_departments...")
            depts = list_departments(temp_dir, "_characters", "char_Gefula")
            print(f"   Departments for char_Gefula: {depts}")
            assert "01_modeling" in depts
            assert "02_rigging" in depts
            
            # Test collect_asset_files
            print("Testing collect_asset_files...")
            all_files = collect_asset_files(temp_dir)
            print(f"   Total asset files found: {len(all_files)}")
            
            # Test with filters
            char_files = collect_asset_files(temp_dir, "_characters")
            print(f"   Character files: {len(char_files)}")
            
            modeling_files = collect_asset_files(temp_dir, "_characters", "01_modeling")
            print(f"   Character modeling files: {len(modeling_files)}")
            
            # Test infer functions
            if all_files:
                filepath, asset_name, dept_name = all_files[0]
                print(f"Testing infer functions with: {filepath}")
                
                inferred_asset = infer_asset_name(filepath)
                inferred_dept = infer_department(filepath)
                print(f"   Inferred asset: {inferred_asset}")
                print(f"   Inferred department: {inferred_dept}")
        
        print("All asset helper tests passed!")
        return True
        
    except Exception as e:
        print(f"Asset helper tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_asset_models():
    """Test the asset table model"""
    print("\nTesting asset table model...")
    
    try:
        from mono_tools.file_manager.file_manager_models import AssetTableModel
        from mono_tools.qt import QtCore, QtGui
        
        # Create model
        model = AssetTableModel()
        
        # Test adding rows
        print("Testing model row addition...")
        model.add_row("char_Gefula", "01_modeling", "v001", "test.hip", ".hip", "/path/to/folder", 1234567890, 1024, "/path/to/test.hip")
        
        # Check row count
        assert model.rowCount() == 1
        
        # Check column headers
        headers = [model.headerData(i, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole) for i in range(model.columnCount())]
        expected_headers = ["Asset Name", "Department", "Ver", "File Name", "Ext", "Folder", "Modified", "Size"]
        assert headers == expected_headers
        
        print("Asset table model tests passed!")
        return True
        
    except Exception as e:
        print(f"Asset model tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Starting Asset Finder Tests...")
    print("=" * 50)
    
    success = True
    
    # Test asset helpers
    if not test_asset_helpers():
        success = False
    
    # Test asset models
    if not test_asset_models():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("All tests passed! Asset Finder is ready to use.")
        print("\nTo test in Houdini:")
        print("   1. Open Houdini")
        print("   2. Run: import mono_tools; mono_tools.open_file_manager()")
        print("   3. Switch to 'Assets' tab")
        print("   4. Set project root to a directory with 01_assets folder")
        print("   5. Use the filtering dropdowns to explore assets")
    else:
        print("Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main()
