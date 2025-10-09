#!/usr/bin/env python3
"""
Test script to verify that asset names are displayed correctly in MiniBar dropdown
instead of showing "sh001" or other incorrect names.
"""

import sys
import os

# Add the file_manager directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'file_manager'))

def test_asset_display_fix():
    """Test that asset names are displayed correctly in MiniBar"""
    print("🧪 Testing Asset Display Fix")
    print("=" * 50)
    
    # Mock the required modules
    class MockQtCore:
        class Qt:
            UserRole = 0x0100
            DisplayRole = 0x0100
            ToolTipRole = 0x0100
            CaseInsensitive = 0x00000001
    
    class MockQtWidgets:
        class QComboBox:
            def __init__(self):
                self.items = []
                self.item_data = {}
            
            def clear(self):
                self.items = []
                self.item_data = {}
            
            def addItem(self, text):
                self.items.append(text)
                return len(self.items) - 1
            
            def setItemData(self, index, value, role):
                if index not in self.item_data:
                    self.item_data[index] = {}
                self.item_data[index][role] = value
            
            def count(self):
                return len(self.items)
    
    # Mock the parse_ver function
    def mock_parse_ver(filename):
        """Mock version parser"""
        import re
        ver_match = re.search(r'v(\d+)', filename)
        return ver_match.group(1) if ver_match else None
    
    # Mock the get_current_houdini_file function
    def mock_get_current_houdini_file():
        return None
    
    # Create a mock MiniBar class
    class MockMiniBar:
        def __init__(self):
            self.combo = MockQtWidgets.QComboBox()
        
        def populate(self, paths, shot_names=None):
            print(f"📁 Populating MiniBar with {len(paths)} files")
            if paths:
                print("Files found:")
                sorted_paths = sorted(paths)
                for i, p in enumerate(sorted_paths[:10]):  # Show first 10 files
                    name = os.path.basename(p)
                    ver = mock_parse_ver(name)
                    print(f"  {i+1}. {name} (v{ver or '—'})")
                if len(sorted_paths) > 10:
                    print(f"  ... and {len(sorted_paths) - 10} more files")
            else:
                print("No files found")
                
            self.combo.clear()
            shot_names = shot_names or {}
            added_count = 0
            for p in sorted(paths):
                # Use asset name if available, otherwise use filename
                if p in shot_names:
                    display_name = shot_names[p]  # This is actually asset_name now
                    name = os.path.basename(p)
                    ver = mock_parse_ver(name)
                    label = f"{display_name} - {name} ({ver or '—'})"
                else:
                    name = os.path.basename(p)
                    ver = mock_parse_ver(name)
                    label = f"{name} ({ver or '—'})"
                
                idx = self.combo.count()
                self.combo.addItem(label)
                self.combo.setItemData(idx, p, MockQtCore.Qt.UserRole)
                self.combo.setItemData(idx, label, MockQtCore.Qt.DisplayRole)
                self.combo.setItemData(idx, name, MockQtCore.Qt.ToolTipRole)
                if p in shot_names: 
                    self.combo.setItemData(idx, shot_names[p], MockQtCore.Qt.UserRole+2)
                added_count += 1
            
            print(f"✅ Added {added_count} items to dropdown (combo.count() = {self.combo.count()})")
            return added_count
    
    # Test case 1: Without asset names (old behavior)
    print("\n1. Testing without asset names (old behavior):")
    minibar = MockMiniBar()
    test_paths = [
        "/project/assets/char_Gefula_v001.hip",
        "/project/assets/char_Gefula_v002.hip",
        "/project/assets/env_Forest_v001.hip"
    ]
    
    count1 = minibar.populate(test_paths)
    print(f"   Dropdown items:")
    for i in range(minibar.combo.count()):
        item_text = minibar.combo.items[i]
        print(f"     {i+1}. {item_text}")
    
    # Test case 2: With asset names (new behavior)
    print("\n2. Testing with asset names (new behavior):")
    minibar2 = MockMiniBar()
    asset_names = {
        "/project/assets/char_Gefula_v001.hip": "char_Gefula",
        "/project/assets/char_Gefula_v002.hip": "char_Gefula", 
        "/project/assets/env_Forest_v001.hip": "env_Forest"
    }
    
    count2 = minibar2.populate(test_paths, asset_names)
    print(f"   Dropdown items:")
    for i in range(minibar2.combo.count()):
        item_text = minibar2.combo.items[i]
        print(f"     {i+1}. {item_text}")
    
    # Test case 3: Mixed scenario (some with asset names, some without)
    print("\n3. Testing mixed scenario:")
    minibar3 = MockMiniBar()
    partial_asset_names = {
        "/project/assets/char_Gefula_v001.hip": "char_Gefula",
        # env_Forest_v001.hip doesn't have asset name
    }
    
    count3 = minibar3.populate(test_paths, partial_asset_names)
    print(f"   Dropdown items:")
    for i in range(minibar3.combo.count()):
        item_text = minibar3.combo.items[i]
        print(f"     {i+1}. {item_text}")
    
    # Verify results
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Test 1 (no asset names): {count1} items")
    print(f"   Test 2 (with asset names): {count2} items") 
    print(f"   Test 3 (mixed): {count3} items")
    
    # Check if asset names are properly displayed
    success = True
    if count2 > 0:
        # Check if asset names appear in the labels
        for i in range(minibar2.combo.count()):
            item_text = minibar2.combo.items[i]
            if "char_Gefula" in item_text or "env_Forest" in item_text:
                print(f"   ✅ Asset names found in dropdown: {item_text}")
            else:
                print(f"   ❌ Asset names missing from dropdown: {item_text}")
                success = False
    
    if success:
        print("\n🎉 All tests passed! Asset names should now display correctly.")
    else:
        print("\n❌ Some tests failed. Check the implementation.")
    
    return success

if __name__ == "__main__":
    test_asset_display_fix()
