"""
Debug script to test subdepartment detection
"""

def test_subdepartment_detection():
    """Test if subdepartments are detected correctly"""
    print("=" * 60)
    print("DEBUG: Subdepartment Detection Test")
    print("=" * 60)
    
    # Test 1: Load config
    print("\n1. Testing config loading...")
    try:
        from mono_tools.file_manager.file_manager_helpers import load_department_config
        config = load_department_config()
        
        if config:
            print(f"✅ Config loaded successfully")
            print(f"   Version: {config.get('version', 'unknown')}")
            print(f"   Departments: {len(config.get('standard_departments', []))}")
        else:
            print(f"❌ Config is None")
            return False
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Check subdepartments for each department
    print("\n2. Testing subdepartment extraction...")
    try:
        from mono_tools.file_manager.file_manager_helpers import get_subdepartments_for_department
        
        if 'standard_departments' in config:
            for dept in config['standard_departments']:
                dept_id = dept['id']
                subdepts = get_subdepartments_for_department(dept_id)
                
                if subdepts:
                    print(f"✅ {dept_id} has {len(subdepts)} subdepartments:")
                    for subdept in subdepts:
                        print(f"     - {subdept['id']}: {subdept['name']}")
                else:
                    print(f"⚪ {dept_id} has no subdepartments")
    except Exception as e:
        print(f"❌ Error getting subdepartments: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Check project structure
    print("\n3. Testing project structure scan...")
    try:
        from mono_tools.qt import QtCore
        s = QtCore.QSettings("Mono", "FileManager")
        
        root = s.value("project_root", "", type=str)
        project = s.value("current_project", "", type=str)
        
        if not root or not project:
            print(f"⚠️  No project configured")
            print(f"   Project Root: {root or 'Not set'}")
            print(f"   Current Project: {project or 'Not set'}")
            print(f"\n   Configure project in MiniBar Settings first!")
            return False
        
        print(f"✅ Project configured:")
        print(f"   Root: {root}")
        print(f"   Project: {project}")
        
        import os
        project_path = os.path.join(root, project)
        
        # Check if 01_assets exists
        assets_dir = os.path.join(project_path, "01_assets")
        if os.path.isdir(assets_dir):
            print(f"\n✅ Assets directory exists: {assets_dir}")
            
            # List types
            from mono_tools.file_manager.file_manager_helpers import scan_project_types
            types = scan_project_types(project_path)
            print(f"   Found {len(types)} types:")
            for type_name, type_path, is_assets in types:
                print(f"     - {type_name}")
            
            # For first type, check department structure
            if types:
                first_type = types[0][0]
                print(f"\n   Checking structure for type: {first_type}")
                
                type_dir = os.path.join(assets_dir, first_type)
                if os.path.isdir(type_dir):
                    # List assets
                    assets = [d for d in os.listdir(type_dir) 
                             if os.path.isdir(os.path.join(type_dir, d)) and not d.startswith('.')]
                    print(f"   Found {len(assets)} assets:")
                    for asset in assets[:3]:  # Show first 3
                        print(f"     - {asset}")
                        
                        # Check departments in this asset
                        asset_path = os.path.join(type_dir, asset)
                        depts = [d for d in os.listdir(asset_path)
                                if os.path.isdir(os.path.join(asset_path, d)) and not d.startswith('.')]
                        
                        print(f"       Departments:")
                        for dept in depts:
                            dept_path = os.path.join(asset_path, dept)
                            
                            # Check for subdepartments
                            subdirs = [d for d in os.listdir(dept_path)
                                      if os.path.isdir(os.path.join(dept_path, d)) and not d.startswith('.')]
                            
                            # Check which are subdepartments (match \d{2}_pattern)
                            import re
                            subdepts_actual = [d for d in subdirs if re.match(r'^\d{2}_', d)]
                            
                            if subdepts_actual:
                                print(f"         - {dept}: {subdepts_actual}")
                            else:
                                print(f"         - {dept}: (no subdepts)")
        else:
            print(f"❌ Assets directory not found: {assets_dir}")
            
    except Exception as e:
        print(f"❌ Error checking project structure: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Simulate menu creation
    print("\n4. Simulating department menu logic...")
    try:
        from mono_tools.file_manager.file_manager_helpers import get_subdepartments_for_department
        
        test_dept = "01_modeling"
        subdepts = get_subdepartments_for_department(test_dept)
        
        print(f"   Testing department: {test_dept}")
        print(f"   Subdepartments from config: {subdepts}")
        
        if subdepts:
            print(f"   ✅ Should show submenu with {len(subdepts)} options")
            print(f"      Menu would show:")
            print(f"        {test_dept} ▶")
            print(f"          ├─ All files")
            print(f"          ├─ ─────────")
            for subdept in subdepts:
                print(f"          └─ {subdept['name']}")
        else:
            print(f"   ⚪ No submenu (no subdepartments in config)")
            
    except Exception as e:
        print(f"❌ Error simulating menu: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("DEBUG TEST COMPLETE")
    print("=" * 60)
    return True


if __name__ == "__main__":
    # Run in Houdini Python Console
    test_subdepartment_detection()

