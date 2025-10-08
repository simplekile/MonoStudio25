"""
Demo script cho Texture Search & Replace Tool
Chạy script này trong Houdini để test chức năng
"""

def demo_texture_search_replace():
    """Demo Texture Search & Replace functionality"""
    try:
        print("🎬 Demo Texture Search & Replace Tool")
        print("=" * 50)
        
        # Import required modules
        try:
            from ..texture_search_replace import show_texture_search_replace
            print("✅ Module imported successfully")
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("💡 Make sure you're running this in Houdini with Mono Studio loaded")
            return False
        
        # Create some test materials with texture paths
        print("\n🔧 Creating test materials...")
        create_demo_materials()
        
        # Show the dialog
        print("\n🔍 Opening Texture Search & Replace dialog...")
        dialog = show_texture_search_replace()
        
        if dialog:
            print("✅ Dialog opened successfully!")
            print("\n💡 Demo instructions:")
            print("   1. Set search pattern: D:/OldProject/")
            print("   2. Set replace pattern: E:/NewProject/")
            print("   3. Select scope: 'Toàn bộ scene'")
            print("   4. Click 'Preview' to see changes")
            print("   5. Click 'Apply Changes' to apply")
            return True
        else:
            print("❌ Failed to open dialog")
            return False
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_demo_materials():
    """Tạo các material demo với texture paths"""
    try:
        import hou
        
        # Tạo material library nếu chưa có
        matlib = hou.node("/mat").node("demo_materials")
        if not matlib:
            matlib = hou.node("/mat").createNode("materiallibrary", "demo_materials")
        
        # Demo materials với các texture paths khác nhau
        demo_materials = [
            {
                "name": "wood_material",
                "textures": {
                    "diffuse": "D:/OldProject/Textures/wood_diffuse_1001.exr",
                    "normal": "D:/OldProject/Textures/wood_normal_1001.exr",
                    "roughness": "D:/OldProject/Textures/wood_roughness_1001.exr",
                    "metallic": "D:/OldProject/Textures/wood_metallic_1001.exr"
                }
            },
            {
                "name": "metal_material",
                "textures": {
                    "basecolor": "D:/OldProject/Assets/metal_basecolor_1002.jpg",
                    "normal": "D:/OldProject/Assets/metal_normal_1002.jpg",
                    "roughness": "D:/OldProject/Assets/metal_roughness_1002.jpg",
                    "metallic": "D:/OldProject/Assets/metal_metallic_1002.jpg"
                }
            },
            {
                "name": "fabric_material",
                "textures": {
                    "diffuse": "D:/OldProject/Textures/fabric_diffuse_1003.png",
                    "normal": "D:/OldProject/Textures/fabric_normal_1003.png",
                    "roughness": "D:/OldProject/Textures/fabric_roughness_1003.png"
                }
            }
        ]
        
        for mat_info in demo_materials:
            # Tạo material builder
            mat_builder = matlib.createNode("rs_usd_material_builder", mat_info["name"])
            
            # Tạo texture nodes
            for tex_type, tex_path in mat_info["textures"].items():
                try:
                    tex_node = mat_builder.createNode("redshift::TextureSampler", f"TS_{tex_type}")
                    tex_node.parm("tex0").set(tex_path)
                    print(f"   ✅ Created {mat_info['name']}.{tex_type}: {tex_path}")
                except Exception as e:
                    print(f"   ⚠️ Could not create {tex_type} node: {e}")
        
        print(f"✅ Created {len(demo_materials)} demo materials")
        
    except Exception as e:
        print(f"❌ Error creating demo materials: {e}")


def demo_regex_patterns():
    """Demo các regex patterns"""
    print("\n🧪 Demo Regex Patterns")
    print("-" * 30)
    
    import re
    
    test_cases = [
        {
            "name": "UDIM to <UDIM>",
            "pattern": r"(\d{4})\.(exr|jpg|png)",
            "replacement": r"<UDIM>.\2",
            "text": "texture_1001.exr"
        },
        {
            "name": "Path replacement",
            "pattern": r"D:/OldProject/",
            "replacement": "E:/NewProject/",
            "text": "D:/OldProject/Textures/wood_diffuse.exr"
        },
        {
            "name": "Case insensitive",
            "pattern": r"oldproject",
            "replacement": "newproject",
            "text": "D:/OldProject/texture.jpg",
            "flags": re.IGNORECASE
        }
    ]
    
    for test in test_cases:
        print(f"\n📝 {test['name']}:")
        print(f"   Pattern: {test['pattern']}")
        print(f"   Replacement: {test['replacement']}")
        print(f"   Input: {test['text']}")
        
        try:
            flags = test.get('flags', 0)
            result = re.sub(test['pattern'], test['replacement'], test['text'], flags=flags)
            print(f"   Result: {result}")
        except Exception as e:
            print(f"   Error: {e}")


def run_full_demo():
    """Chạy demo đầy đủ"""
    print("🚀 Mono Studio - Texture Search & Replace Demo")
    print("=" * 60)
    
    # Demo 1: Basic functionality
    print("\n1️⃣ Basic Functionality Demo")
    demo_texture_search_replace()
    
    # Demo 2: Regex patterns
    print("\n2️⃣ Regex Patterns Demo")
    demo_regex_patterns()
    
    print("\n" + "=" * 60)
    print("✅ Demo completed!")
    print("💡 Check the Mono Studio menu for 'Texture Search & Replace'")


if __name__ == "__main__":
    run_full_demo()
