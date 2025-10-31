"""
Debug why submenu is not showing
Run this in Houdini Python Console
"""

def debug_submenu_issue():
    """Complete debug of submenu not showing"""
    print("\n" + "=" * 70)
    print("DEBUG: Why Submenu Not Showing?")
    print("=" * 70)
    
    # Step 1: Check config file
    print("\n[STEP 1] Checking config file...")
    try:
        from mono_tools.file_manager.file_manager_helpers import load_department_config
        config = load_department_config()
        
        if not config:
            print("❌ Config is None!")
            return False
        
        print(f"✅ Config loaded")
        print(f"   Keys: {list(config.keys())}")
        
        # Check if shot_departments exists
        if 'shot_departments' not in config:
            print("❌ 'shot_departments' key NOT found in config!")
            print(f"   Available keys: {list(config.keys())}")
            return False
        
        print(f"✅ 'shot_departments' key found")
        shot_depts = config['shot_departments']
        print(f"   Number of shot departments: {len(shot_depts)}")
        
        # Check 02_sim specifically
        sim_dept = None
        for dept in shot_depts:
            print(f"   - {dept['id']}: {dept.get('name', 'N/A')}")
            if dept['id'] == '02_sim':
                sim_dept = dept
        
        if not sim_dept:
            print("❌ Department '02_sim' NOT found in config!")
            return False
        
        print(f"\n✅ Found 02_sim department:")
        print(f"   ID: {sim_dept['id']}")
        print(f"   Name: {sim_dept['name']}")
        
        # Check subdepartments
        if 'subdepartments' not in sim_dept:
            print("❌ 'subdepartments' key NOT found in 02_sim!")
            print(f"   Keys in 02_sim: {list(sim_dept.keys())}")
            return False
        
        subdepts = sim_dept['subdepartments']
        print(f"✅ Subdepartments field found: {len(subdepts)} subdepts")
        for subdept in subdepts:
            print(f"      - {subdept['id']}: {subdept['name']}")
            
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 2: Test get_subdepartments_for_department function
    print("\n[STEP 2] Testing get_subdepartments_for_department()...")
    try:
        from mono_tools.file_manager.file_manager_helpers import get_subdepartments_for_department
        
        result = get_subdepartments_for_department("02_sim")
        
        if not result:
            print("❌ Function returned empty list!")
            print("   This means function is not finding subdepartments")
            
            # Debug the function
            print("\n   Debugging function logic...")
            config = load_department_config()
            print(f"   Config exists: {config is not None}")
            print(f"   'shot_departments' in config: {'shot_departments' in config}")
            
            if config and 'shot_departments' in config:
                for dept in config['shot_departments']:
                    if dept['id'] == '02_sim':
                        print(f"   Found 02_sim in config!")
                        print(f"   subdepartments: {dept.get('subdepartments', [])}")
                        break
            return False
        
        print(f"✅ Function returned {len(result)} subdepartments:")
        for s in result:
            print(f"      - {s['id']}: {s['name']}")
            
    except Exception as e:
        print(f"❌ Error calling function: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Check MiniBar current state
    print("\n[STEP 3] Checking MiniBar state...")
    try:
        from mono_tools.qt import QtCore
        s = QtCore.QSettings("Mono", "FileManager")
        
        current_type = s.value("minibar_type", "", type=str)
        root = s.value("project_root", "", type=str)
        project = s.value("current_project", "", type=str)
        
        print(f"   Current Type: {current_type or 'Not set'}")
        print(f"   Project Root: {root or 'Not set'}")
        print(f"   Project: {project or 'Not set'}")
        
        if current_type != "Shots":
            print(f"⚠️  Current type is '{current_type}', not 'Shots'!")
            print("   You need to select Type: Shots first!")
        else:
            print(f"✅ Type is 'Shots'")
            
    except Exception as e:
        print(f"⚠️  Error checking MiniBar state: {e}")
    
    # Step 4: Simulate menu logic
    print("\n[STEP 4] Simulating department menu logic...")
    try:
        from mono_tools.file_manager.file_manager_helpers import get_subdepartments_for_department
        
        dept = "02_sim"
        subdepts = get_subdepartments_for_department(dept)
        
        print(f"   Department: {dept}")
        print(f"   Subdepartments found: {len(subdepts)}")
        
        if subdepts:
            print(f"\n   ✅ SHOULD show submenu:")
            print(f"      dept_submenu = menu.addMenu('💨 {dept}')")
            print(f"      main_action = dept_submenu.addAction('📁 All files')")
            print(f"      dept_submenu.addSeparator()")
            for subdept in subdepts:
                print(f"      subdept_action = dept_submenu.addAction('  └─ {subdept['name']}')")
        else:
            print(f"\n   ❌ NO submenu (no subdepartments found)")
            print(f"      action = menu.addAction('💨 {dept}')")
            
    except Exception as e:
        print(f"❌ Error simulating menu: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 5: Check actual MiniBar code
    print("\n[STEP 5] Checking if MiniBar is using correct logic...")
    try:
        # Try to find MiniBar instance
        from mono_tools.qt import QtWidgets
        import hou
        
        main_window = hou.qt.mainWindow()
        minibar = None
        
        # Find MiniBar widget
        for child in main_window.findChildren(QtWidgets.QWidget):
            if child.objectName() == "MonoMiniBar":
                minibar = child
                break
        
        if not minibar:
            print("⚠️  MiniBar not found!")
            print("   You need to open MiniBar first:")
            print("   from mono_tools import show_mono_minibar")
            print("   show_mono_minibar()")
        else:
            print("✅ MiniBar found")
            print(f"   Current type: {getattr(minibar, 'current_type', 'Not set')}")
            print(f"   Current dept: {getattr(minibar, 'current_dept', 'Not set')}")
            print(f"   Current subdept: {getattr(minibar, 'current_subdept', 'Not set')}")
            
    except Exception as e:
        print(f"⚠️  Error checking MiniBar: {e}")
    
    print("\n" + "=" * 70)
    print("DEBUG COMPLETE")
    print("=" * 70)
    
    # Recommendations
    print("\n[RECOMMENDATIONS]")
    print("1. If config loaded correctly but function returns empty:")
    print("   → Restart Houdini to reload Python modules")
    print("")
    print("2. If MiniBar not found:")
    print("   → Run: from mono_tools import show_mono_minibar; show_mono_minibar()")
    print("")
    print("3. If Type is not 'Shots':")
    print("   → Click Type button and select 'Shots'")
    print("")
    print("4. If everything looks correct but still no submenu:")
    print("   → Close and reopen MiniBar")
    print("   → Or restart Houdini")
    
    return True

# Run it
if __name__ == "__main__":
    debug_submenu_issue()

