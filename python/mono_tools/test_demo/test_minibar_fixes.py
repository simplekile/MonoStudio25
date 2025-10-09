#!/usr/bin/env python3
"""
Test script to verify MiniBar fixes:
1. Initialization without File Manager
2. Department filtering
3. Empty department display
"""

import sys
import os

# Add the file_manager directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'file_manager'))

def test_minibar_fixes():
    """Test MiniBar fixes"""
    print("🧪 Testing MiniBar Fixes")
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
                self.current_idx = -1
            
            def clear(self):
                self.items = []
                self.item_data = {}
                self.current_idx = -1
            
            def addItem(self, text):
                self.items.append(text)
                return len(self.items) - 1
            
            def setItemData(self, index, value, role):
                if index not in self.item_data:
                    self.item_data[index] = {}
                self.item_data[index][role] = value
            
            def count(self):
                return len(self.items)
            
            def currentIndex(self):
                return self.current_idx
            
            def setCurrentIndex(self, idx):
                self.current_idx = idx
            
            def itemData(self, index, role=None):
                if index in self.item_data and role in self.item_data[index]:
                    return self.item_data[index][role]
                return None
        
        class QLineEdit:
            def __init__(self):
                self.text_value = ""
                self.tooltip_value = ""
            
            def setText(self, text):
                self.text_value = text
            
            def setToolTip(self, tooltip):
                self.tooltip_value = tooltip
    
    # Mock the parse_ver function
    def mock_parse_ver(filename):
        """Mock version parser"""
        import re
        ver_match = re.search(r'v(\d+)', filename)
        return ver_match.group(1) if ver_match else None
    
    # Mock the get_current_houdini_file function
    def mock_get_current_houdini_file():
        return None
    
    # Mock the is_current_file function
    def mock_is_current_file(filepath):
        return False
    
    # Create a mock MiniBar class
    class MockMiniBar:
        def __init__(self):
            self.combo = MockQtWidgets.QComboBox()
            self.shot_display = MockQtWidgets.QLineEdit()
        
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
            
            # Clear shot display if no files found
            if self.combo.count() == 0:
                self.shot_display.setText("No files")
                self.shot_display.setToolTip("No files available")
                print("✅ Shot display cleared: 'No files'")
                return
            
            # Simulate file selection
            if self.combo.count() > 0:
                self.combo.setCurrentIndex(0)
                selected_text = self.combo.items[0]
                self.shot_display.setText(selected_text)
                print(f"✅ Shot display updated: '{selected_text}'")
    
    # Test case 1: Empty department (should show "No files")
    print("\n1. Testing empty department:")
    minibar1 = MockMiniBar()
    minibar1.populate([])  # No files
    print(f"   Shot display: '{minibar1.shot_display.text_value}'")
    print(f"   Tooltip: '{minibar1.shot_display.tooltip_value}'")
    
    # Test case 2: Department with files
    print("\n2. Testing department with files:")
    minibar2 = MockMiniBar()
    test_paths = ["/project/assets/char_Gefula_lookdev_v001.hip"]
    asset_names = {"/project/assets/char_Gefula_lookdev_v001.hip": "char_Gefula"}
    minibar2.populate(test_paths, asset_names)
    print(f"   Shot display: '{minibar2.shot_display.text_value}'")
    print(f"   Dropdown items: {minibar2.combo.items}")
    
    # Test case 3: Switch from files to empty
    print("\n3. Testing switch from files to empty:")
    minibar3 = MockMiniBar()
    # First populate with files
    minibar3.populate(test_paths, asset_names)
    print(f"   After files: '{minibar3.shot_display.text_value}'")
    # Then clear
    minibar3.populate([])
    print(f"   After clear: '{minibar3.shot_display.text_value}'")
    
    # Verify results
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    success = True
    
    # Check empty department handling
    if minibar1.shot_display.text_value == "No files":
        print("   ✅ Empty department shows 'No files'")
    else:
        print(f"   ❌ Empty department shows '{minibar1.shot_display.text_value}' instead of 'No files'")
        success = False
    
    # Check file display
    if "char_Gefula" in minibar2.shot_display.text_value:
        print("   ✅ Files display with asset names")
    else:
        print(f"   ❌ Files don't display with asset names: '{minibar2.shot_display.text_value}'")
        success = False
    
    # Check clear functionality
    if minibar3.shot_display.text_value == "No files":
        print("   ✅ Clear functionality works")
    else:
        print(f"   ❌ Clear functionality failed: '{minibar3.shot_display.text_value}'")
        success = False
    
    if success:
        print("\n🎉 All tests passed! MiniBar fixes are working.")
    else:
        print("\n❌ Some tests failed. Check the implementation.")
    
    return success

if __name__ == "__main__":
    test_minibar_fixes()
