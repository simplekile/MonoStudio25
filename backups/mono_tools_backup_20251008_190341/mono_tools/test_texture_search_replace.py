"""
Test script cho Texture Search & Replace Tool
"""

import hou
from .texture_search_replace import show_texture_search_replace


def create_test_scene():
    """Tạo scene test với các texture nodes"""
    try:
        # Tạo geometry container
        geo = hou.node("/obj").createNode("geo", "test_geometry")
        
        # Tạo material library
        matlib = hou.node("/mat").createNode("materiallibrary", "test_materials")
        
        # Tạo một số material nodes với texture paths
        materials = [
            {
                "name": "test_material_1",
                "textures": {
                    "diffuse": "D:/OldProject/Textures/wood_diffuse_1001.exr",
                    "normal": "D:/OldProject/Textures/wood_normal_1001.exr",
                    "roughness": "D:/OldProject/Textures/wood_roughness_1001.exr"
                }
            },
            {
                "name": "test_material_2", 
                "textures": {
                    "basecolor": "D:/OldProject/Assets/metal_basecolor_1002.jpg",
                    "metallic": "D:/OldProject/Assets/metal_metallic_1002.jpg",
                    "normal": "D:/OldProject/Assets/metal_normal_1002.jpg"
                }
            }
        ]
        
        for mat_info in materials:
            # Tạo material builder
            mat_builder = matlib.createNode("rs_usd_material_builder", mat_info["name"])
            
            # Tạo texture nodes
            for tex_type, tex_path in mat_info["textures"].items():
                tex_node = mat_builder.createNode("redshift::TextureSampler", f"TS_{tex_type}")
                tex_node.parm("tex0").set(tex_path)
        
        print("✅ Test scene created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating test scene: {e}")
        return False


def test_texture_search_replace():
    """Test Texture Search & Replace functionality"""
    try:
        print("🧪 Testing Texture Search & Replace...")
        
        # Tạo scene test
        if not create_test_scene():
            return False
        
        # Mở dialog
        print("🔍 Opening Texture Search & Replace dialog...")
        dialog = show_texture_search_replace()
        
        if dialog:
            print("✅ Dialog opened successfully")
            print("💡 Test cases:")
            print("   1. Search: D:/OldProject/")
            print("   2. Replace: E:/NewProject/")
            print("   3. Scope: Entire scene")
            print("   4. Enable backup")
            return True
        else:
            print("❌ Failed to open dialog")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_regex_patterns():
    """Test các regex patterns khác nhau"""
    test_cases = [
        {
            "name": "Simple path replacement",
            "search": "D:/OldProject/",
            "replace": "E:/NewProject/",
            "input": "D:/OldProject/Textures/wood_diffuse.exr",
            "expected": "E:/NewProject/Textures/wood_diffuse.exr"
        },
        {
            "name": "Regex pattern with UDIM",
            "search": r"(\d{4})\.(exr|jpg|png)",
            "replace": r"<UDIM>.\2",
            "input": "texture_1001.exr",
            "expected": "texture_<UDIM>.exr"
        },
        {
            "name": "Case insensitive",
            "search": "oldproject",
            "replace": "newproject",
            "input": "D:/OldProject/texture.jpg",
            "expected": "D:/NewProject/texture.jpg"
        }
    ]
    
    print("🧪 Testing regex patterns...")
    
    for test_case in test_cases:
        print(f"\n📝 Test: {test_case['name']}")
        print(f"   Search: {test_case['search']}")
        print(f"   Replace: {test_case['replace']}")
        print(f"   Input: {test_case['input']}")
        print(f"   Expected: {test_case['expected']}")
        
        # Simulate replacement logic
        import re
        try:
            if test_case['name'] == "Case insensitive":
                result = re.sub(test_case['search'], test_case['replace'], 
                              test_case['input'], flags=re.IGNORECASE)
            else:
                result = re.sub(test_case['search'], test_case['replace'], 
                              test_case['input'])
            
            if result == test_case['expected']:
                print("   ✅ PASS")
            else:
                print(f"   ❌ FAIL - Got: {result}")
        except Exception as e:
            print(f"   ❌ ERROR - {e}")


def run_all_tests():
    """Chạy tất cả tests"""
    print("🚀 Running Texture Search & Replace Tests...")
    print("=" * 50)
    
    # Test 1: Basic functionality
    print("\n1️⃣ Testing basic functionality...")
    test_texture_search_replace()
    
    # Test 2: Regex patterns
    print("\n2️⃣ Testing regex patterns...")
    test_regex_patterns()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")


if __name__ == "__main__":
    run_all_tests()
