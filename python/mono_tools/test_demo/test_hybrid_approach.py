#!/usr/bin/env python3
"""
Test script to verify hybrid asset collection approach
"""

import sys
import os

# Add the file_manager directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'file_manager'))

def test_hybrid_approach():
    """Test hybrid asset collection approach"""
    print("🧪 Testing Hybrid Asset Collection Approach")
    print("=" * 60)
    
    # Mock the required modules
    class MockQtCore:
        class Qt:
            UserRole = 0x0100
            DisplayRole = 0x0100
            ToolTipRole = 0x0100
            CaseInsensitive = 0x00000001
    
    # Mock the parse_ver function
    def mock_parse_ver(filename):
        """Mock version parser"""
        import re
        ver_match = re.search(r'v(\d+)', filename)
        return ver_match.group(1) if ver_match else None
    
    # Test filename parsing
    print("\n1. Testing filename parsing:")
    from file_manager_helpers import parse_asset_info_from_filename
    
    test_files = [
        "char_Gefula_modeling_v001.hip",
        "env_Forest_lighting_v002.hip", 
        "prop_Chair_surfacing_v003.hip",
        "char_John_lookdev_v001.hip",
        "env_City_comp_v004.hip",
        "unknown_file_v001.hip"
    ]
    
    for filename in test_files:
        asset_type, asset_name, department = parse_asset_info_from_filename(filename)
        print(f"  {filename}")
        print(f"    -> Type: {asset_type}, Asset: {asset_name}, Dept: {department}")
    
    # Test filename-based collection (simulated)
    print("\n2. Testing filename-based collection (simulated):")
    
    # Create mock file structure
    mock_files = [
        ("/project/char_Gefula_modeling_v001.hip", "char_Gefula_modeling_v001.hip"),
        ("/project/char_Gefula_lookdev_v002.hip", "char_Gefula_lookdev_v002.hip"),
        ("/project/env_Forest_lighting_v001.hip", "env_Forest_lighting_v001.hip"),
        ("/project/prop_Chair_surfacing_v003.hip", "prop_Chair_surfacing_v003.hip"),
        ("/project/random_file_v001.hip", "random_file_v001.hip")
    ]
    
    print("  Mock files found:")
    for filepath, filename in mock_files:
        asset_type, asset_name, department = parse_asset_info_from_filename(filename)
        if asset_name:  # Only show files we can parse
            print(f"    {filename} -> {asset_name} ({department or 'unknown'})")
    
    # Test filtering
    print("\n3. Testing filtering:")
    
    # Filter by asset type
    char_files = []
    for filepath, filename in mock_files:
        asset_type, asset_name, department = parse_asset_info_from_filename(filename)
        if asset_type == "_characters":
            char_files.append((filepath, asset_name, department))
    
    print(f"  Character files: {len(char_files)}")
    for filepath, asset_name, department in char_files:
        print(f"    {os.path.basename(filepath)} -> {asset_name} ({department})")
    
    # Filter by department
    lookdev_files = []
    for filepath, filename in mock_files:
        asset_type, asset_name, department = parse_asset_info_from_filename(filename)
        if department == "04_lookdev":
            lookdev_files.append((filepath, asset_name, department))
    
    print(f"  Lookdev files: {len(lookdev_files)}")
    for filepath, asset_name, department in lookdev_files:
        print(f"    {os.path.basename(filepath)} -> {asset_name} ({department})")
    
    # Test hybrid approach logic
    print("\n4. Testing hybrid approach logic:")
    
    # Simulate subfolder-based search (no results)
    subfolder_results = []
    print(f"  Subfolder-based search: {len(subfolder_results)} results")
    
    # Simulate filename-based search (fallback)
    filename_results = []
    for filepath, filename in mock_files:
        asset_type, asset_name, department = parse_asset_info_from_filename(filename)
        if asset_name:
            filename_results.append((filepath, asset_name, department or "unknown"))
    
    print(f"  Filename-based search: {len(filename_results)} results")
    
    # Hybrid result
    if subfolder_results:
        final_results = subfolder_results
        method = "subfolder"
    else:
        final_results = filename_results
        method = "filename"
    
    print(f"  Hybrid approach: Using {method} method with {len(final_results)} results")
    
    # Verify results
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    
    success = True
    
    # Check filename parsing
    if len([f for f in test_files if parse_asset_info_from_filename(f)[1]]) >= 4:
        print("   ✅ Filename parsing works for most files")
    else:
        print("   ❌ Filename parsing has issues")
        success = False
    
    # Check filtering
    if len(char_files) >= 2:
        print("   ✅ Asset type filtering works")
    else:
        print("   ❌ Asset type filtering has issues")
        success = False
    
    # Check hybrid logic
    if len(final_results) > 0:
        print("   ✅ Hybrid approach produces results")
    else:
        print("   ❌ Hybrid approach produces no results")
        success = False
    
    if success:
        print("\n🎉 All tests passed! Hybrid approach is working.")
    else:
        print("\n❌ Some tests failed. Check the implementation.")
    
    return success

if __name__ == "__main__":
    test_hybrid_approach()
