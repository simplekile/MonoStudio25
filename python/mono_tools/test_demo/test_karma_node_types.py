#!/usr/bin/env python3
"""
Test script để kiểm tra node types cho Karma Material Builder trong Houdini

Cách sử dụng:
1. Mở Houdini
2. Chạy script này trong Python Shell hoặc hscript
3. Xem kết quả để biết node type chính xác
"""

import hou

def test_karma_node_types():
    """Test các node types có thể dùng cho Karma Material"""
    
    print("=" * 80)
    print("KIỂM TRA NODE TYPES CHO KARMA MATERIAL BUILDER")
    print("=" * 80)
    print()
    
    # Node types cần test
    node_types_to_test = [
        "MaterialBuilder",
        "karma::MaterialBuilder", 
        "Material::2.0",
        "Material",
        "Material::1.0",
        "karma::Material",
        "vop::MaterialBuilder",
    ]
    
    print("📋 DANH SÁCH NODE TYPES CẦN TEST:")
    for i, nt in enumerate(node_types_to_test, 1):
        print(f"  {i}. {nt}")
    print()
    
    # Test tạo node trong /mat context
    try:
        mat_context = hou.node("/mat")
        if mat_context is None:
            print("❌ Không tìm thấy /mat context!")
            print("💡 Tạo /mat context trước khi test")
            return
        
        print("✅ Tìm thấy /mat context")
        print()
        
        results = {}
        
        for node_type in node_types_to_test:
            print(f"🔍 Testing: {node_type}")
            try:
                # Tạo test node
                test_node = mat_context.createNode(node_type, f"test_{node_type.replace('::', '_')}")
                
                if test_node:
                    node_type_info = test_node.type()
                    type_name = node_type_info.name()
                    category = node_type_info.category()
                    is_network = test_node.isNetwork()
                    
                    results[node_type] = {
                        "success": True,
                        "type_name": type_name,
                        "category": category.name() if category else "Unknown",
                        "is_network": is_network,
                        "description": node_type_info.description() if hasattr(node_type_info, 'description') else "N/A"
                    }
                    
                    print(f"  ✅ THÀNH CÔNG!")
                    print(f"     - Type Name: {type_name}")
                    print(f"     - Category: {category.name() if category else 'Unknown'}")
                    print(f"     - Is Network: {is_network}")
                    print(f"     - Description: {node_type_info.description() if hasattr(node_type_info, 'description') else 'N/A'}")
                    
                    # Xóa test node
                    test_node.destroy()
                else:
                    results[node_type] = {"success": False, "error": "createNode returned None"}
                    print(f"  ❌ createNode trả về None")
                    
            except Exception as e:
                results[node_type] = {"success": False, "error": str(e)}
                print(f"  ❌ LỖI: {e}")
            
            print()
        
        # Tóm tắt
        print("=" * 80)
        print("📊 TÓM TẮT KẾT QUẢ:")
        print("=" * 80)
        print()
        
        successful = [nt for nt, r in results.items() if r.get("success")]
        failed = [nt for nt, r in results.items() if not r.get("success")]
        
        if successful:
            print("✅ NODE TYPES HOẠT ĐỘNG:")
            for nt in successful:
                r = results[nt]
                print(f"  • {nt}")
                print(f"    - Type Name: {r['type_name']}")
                print(f"    - Is Network: {r['is_network']}")
                print(f"    - Category: {r['category']}")
                print()
        
        if failed:
            print("❌ NODE TYPES KHÔNG HOẠT ĐỘNG:")
            for nt in failed:
                r = results[nt]
                print(f"  • {nt}: {r.get('error', 'Unknown error')}")
            print()
        
        # Khuyến nghị
        print("=" * 80)
        print("💡 KHUYẾN NGHỊ:")
        print("=" * 80)
        
        if successful:
            # Tìm node type tốt nhất (MaterialBuilder network node)
            best = None
            for nt in successful:
                r = results[nt]
                if r.get("is_network") and "MaterialBuilder" in r.get("type_name", ""):
                    best = nt
                    break
            
            if best:
                print(f"✅ Node type được khuyến nghị: {best}")
                print(f"   - Đây là network node, có thể tạo child nodes bên trong")
            else:
                # Tìm network node đầu tiên
                for nt in successful:
                    r = results[nt]
                    if r.get("is_network"):
                        print(f"✅ Node type được khuyến nghị: {nt}")
                        print(f"   - Đây là network node, có thể tạo child nodes bên trong")
                        break
                else:
                    print(f"⚠️  Tất cả node types đều là single nodes (không phải network)")
                    print(f"   - Khuyến nghị dùng node type đầu tiên hoạt động: {successful[0]}")
        else:
            print("❌ KHÔNG CÓ NODE TYPE NÀO HOẠT ĐỘNG!")
            print("   - Kiểm tra lại version Houdini")
            print("   - Đảm bảo Karma renderer được cài đặt")
        
        print()
        print("=" * 80)
        print("📚 TÀI LIỆU CHÍNH THỨC:")
        print("=" * 80)
        print("1. Houdini Documentation:")
        print("   https://www.sidefx.com/docs/houdini/")
        print()
        print("2. MaterialBuilder Node:")
        print("   https://www.sidefx.com/docs/houdini/nodes/vop/materialbuilder.html")
        print()
        print("3. Material Node (Karma):")
        print("   https://www.sidefx.com/docs/houdini/nodes/vop/material.html")
        print()
        print("4. Creating Nodes via Python:")
        print("   https://www.sidefx.com/docs/houdini/hom/hou/Node.html#createNode")
        print()
        
    except Exception as e:
        print(f"❌ LỖI CHUNG: {e}")
        import traceback
        traceback.print_exc()


def list_all_material_nodes():
    """Liệt kê tất cả node types liên quan đến Material"""
    print("=" * 80)
    print("DANH SÁCH TẤT CẢ MATERIAL-RELATED NODE TYPES")
    print("=" * 80)
    print()
    
    try:
        # Lấy tất cả node types trong /mat context
        mat_category = hou.nodeTypeCategory("/mat")
        node_types = mat_category.nodeTypes()
        
        material_types = []
        for node_type in node_types:
            name = node_type.name()
            if "material" in name.lower() or "karma" in name.lower():
                material_types.append(node_type)
        
        if material_types:
            print(f"📋 Tìm thấy {len(material_types)} node types:")
            print()
            for nt in sorted(material_types, key=lambda x: x.name()):
                print(f"  • {nt.name()}")
                print(f"    - Category: {nt.category().name()}")
                desc = nt.description() if hasattr(nt, 'description') else "N/A"
                print(f"    - Description: {desc[:100]}...")
                print()
        else:
            print("❌ Không tìm thấy node types nào liên quan đến Material/Karma")
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        # Test các node types
        test_karma_node_types()
        
        print("\n" + "=" * 80 + "\n")
        
        # List tất cả material nodes
        list_all_material_nodes()
        
    except ImportError:
        print("❌ Houdini Python module (hou) không tìm thấy!")
        print("💡 Chạy script này trong Houdini Python Shell")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
