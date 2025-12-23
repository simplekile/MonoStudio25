#!/usr/bin/env python3
"""
Script để kiểm tra node Karma Material Builder đã được tạo trong scene

LƯU Ý: Material Builder trong Houdini 21+ chủ yếu dùng trong SOLARIS (/stage), 
không phải /mat context truyền thống!

Cách sử dụng:
1. Tạo Material Builder trong Solaris (/stage) hoặc /mat
2. Chạy script này trong Houdini Python Shell
3. Script sẽ tìm và hiển thị thông tin về node đó
"""

import hou

def check_karma_material_builder(node_path=None, check_solaris=True):
    """
    Kiểm tra node Material Builder trong scene
    
    Args:
        node_path (str, optional): Đường dẫn cụ thể đến node (vd: "/mat/my_material")
                                  Nếu None, sẽ tìm tất cả Material Builder nodes
    """
    
    print("=" * 80)
    print("KIỂM TRA KARMA MATERIAL BUILDER NODE")
    print("=" * 80)
    print()
    print("ℹ️  LƯU Ý: Material Builder thường dùng trong SOLARIS (/stage), không phải /mat!")
    print()
    
    try:
        nodes_to_check = []
        
        # Nếu có node_path cụ thể
        if node_path:
            node = hou.node(node_path)
            if node:
                nodes_to_check.append(node)
            else:
                print(f"❌ Không tìm thấy node: {node_path}")
                return
        else:
            # Tìm trong cả /mat và /stage (Solaris)
            print("🔍 Đang tìm Material Builder nodes...")
            print()
            
            contexts_to_check = []
            
            # 1. Kiểm tra /stage (Solaris) - QUAN TRỌNG!
            if check_solaris:
                stage_context = hou.node("/stage")
                if stage_context:
                    print("✅ Tìm thấy /stage context (Solaris)")
                    contexts_to_check.append(("/stage", stage_context))
                else:
                    print("⚠️  Không tìm thấy /stage context (Solaris)")
            
            # 2. Kiểm tra /mat (traditional)
            mat_context = hou.node("/mat")
            if mat_context:
                print("✅ Tìm thấy /mat context (traditional)")
                contexts_to_check.append(("/mat", mat_context))
            else:
                print("⚠️  Không tìm thấy /mat context")
            
            print()
            
            if not contexts_to_check:
                print("❌ Không tìm thấy context nào!")
                print("💡 Tạo /mat hoặc /stage context trước")
                return
            
            # Tìm nodes trong tất cả contexts
            for context_name, context_node in contexts_to_check:
                print(f"🔍 Đang tìm trong {context_name}...")
                
                for child in context_node.children():
                    node_type = child.type()
                    type_name = node_type.name()
                    
                    # Kiểm tra nếu là Material Builder hoặc Material node
                    if ("MaterialBuilder" in type_name or 
                        "Material" in type_name or
                        "karma" in type_name.lower() or
                        "usdmaterial" in type_name.lower()):
                        nodes_to_check.append(child)
                        print(f"  ✓ Tìm thấy: {child.path()}")
            
            print()
            
            if not nodes_to_check:
                print("⚠️  Không tìm thấy Material Builder nodes nào!")
                print()
                print("💡 CÁCH TẠO MATERIAL BUILDER:")
                print()
                print("1. TRONG SOLARIS (/stage) - KHUYẾN NGHỊ:")
                print("   - Mở Solaris (Stage) pane")
                print("   - Tab menu → Material → Material Library")
                print("   - Hoặc Python:")
                print("     stage = hou.node('/stage')")
                print("     matlib = stage.createNode('materiallibrary')")
                print("     mat_builder = matlib.createNode('MaterialBuilder', 'my_material')")
                print()
                print("2. TRONG /MAT (traditional):")
                print("   - Tab menu → Material → Material Builder")
                print("   - Hoặc Python:")
                print("     matlib = hou.node('/mat')")
                print("     mat_builder = matlib.createNode('MaterialBuilder', 'my_material')")
                print()
                print("⚠️  LƯU Ý: Material Builder trong Houdini 21+ chủ yếu dùng cho USD/Solaris!")
                return
        
        # Kiểm tra từng node
        for i, node in enumerate(nodes_to_check, 1):
            print("=" * 80)
            print(f"NODE {i}: {node.path()}")
            print("=" * 80)
            print()
            
            # Basic info
            print("📋 THÔNG TIN CƠ BẢN:")
            print(f"  • Path: {node.path()}")
            print(f"  • Name: {node.name()}")
            print(f"  • Type: {node.type().name()}")
            print(f"  • Category: {node.type().category().name()}")
            
            # Context info
            context_path = node.path().split('/')[1] if '/' in node.path() else "unknown"
            if context_path == "stage":
                print(f"  • Context: ⭐ SOLARIS (/stage) - USD Materials")
            elif context_path == "mat":
                print(f"  • Context: /mat (Traditional Materials)")
            else:
                print(f"  • Context: {context_path}")
            print()
            
            # Network info
            is_network = node.isNetwork()
            print("🔗 THÔNG TIN NETWORK:")
            print(f"  • Is Network Node: {is_network}")
            
            if is_network:
                child_count = len(node.children())
                print(f"  • Child Nodes Count: {child_count}")
                
                if child_count > 0:
                    print(f"  • Child Nodes:")
                    for child in node.children():
                        print(f"      - {child.name()} ({child.type().name()})")
            print()
            
            # Type details
            node_type = node.type()
            print("📝 CHI TIẾT NODE TYPE:")
            
            # Description
            try:
                desc = node_type.description()
                if desc:
                    print(f"  • Description: {desc[:200]}...")
            except:
                print(f"  • Description: N/A")
            
            # Inputs/Outputs
            print(f"  • Input Count: {len(node.inputs())}")
            print(f"  • Output Count: {len(node.outputs())}")
            
            if node.inputs():
                print(f"  • Input Names:")
                for idx, input_node in enumerate(node.inputs()):
                    if input_node:
                        print(f"      [{idx}] {input_node.name()}")
            
            if node.outputs():
                print(f"  • Output Names:")
                for idx, output_node in enumerate(node.outputs()):
                    if output_node:
                        print(f"      [{idx}] {output_node.name()}")
            print()
            
            # Parameters
            print("⚙️  PARAMETERS (First 10):")
            parms = node.parms()
            if parms:
                for parm in parms[:10]:
                    try:
                        value = parm.eval()
                        print(f"  • {parm.name()}: {value}")
                    except:
                        print(f"  • {parm.name()}: (error reading)")
                
                if len(parms) > 10:
                    print(f"  ... và {len(parms) - 10} parameters khác")
            else:
                print("  (No parameters)")
            print()
            
            # Kiểm tra đặc biệt cho Material Builder
            print("🎨 PHÂN TÍCH MATERIAL BUILDER:")
            type_name = node_type.name()
            
            if "MaterialBuilder" in type_name:
                print("  ✅ Đây là MaterialBuilder node")
                
                if is_network:
                    print("  ✅ Đây là network node - có thể chứa child nodes")
                    
                    # Kiểm tra có Material node bên trong không
                    material_nodes = [c for c in node.children() if "Material" in c.type().name()]
                    if material_nodes:
                        print(f"  ✅ Tìm thấy {len(material_nodes)} Material node(s) bên trong:")
                        for mat_node in material_nodes:
                            print(f"      - {mat_node.name()} ({mat_node.type().name()})")
                    else:
                        print("  ⚠️  Không tìm thấy Material node bên trong")
                        print("  💡 Tạo Material node bên trong để sử dụng")
                    
                    # Kiểm tra texture nodes
                    texture_nodes = [c for c in node.children() if "Texture" in c.type().name()]
                    if texture_nodes:
                        print(f"  ✅ Tìm thấy {len(texture_nodes)} Texture node(s):")
                        for tex_node in texture_nodes:
                            print(f"      - {tex_node.name()} ({tex_node.type().name()})")
                
            elif "Material" in type_name and not is_network:
                print("  ⚠️  Đây là Material node (single node, không phải network)")
                print("  💡 Để tạo material graph phức tạp, dùng MaterialBuilder thay vì Material")
                print("  ✅ Có thể set textures trực tiếp qua parameters")
            
            elif "subnet" in type_name.lower():
                print("  ⚠️  Đây là subnet node (fallback option)")
                print("  💡 Nên dùng MaterialBuilder cho material creation")
            
            print()
            
            # Kết luận
            print("💡 KẾT LUẬN:")
            if "MaterialBuilder" in type_name and is_network:
                print("  ✅ Node này phù hợp để tạo material graph")
                print("  ✅ Có thể tạo Material và Texture nodes bên trong")
            elif "Material" in type_name and not is_network:
                print("  ✅ Node này phù hợp cho material đơn giản")
                print("  ⚠️  Không thể tạo child nodes, chỉ set parameters")
            else:
                print("  ⚠️  Node type này có thể không phải Material Builder chuẩn")
            
            print()
            print()
        
        # Tổng kết
        print("=" * 80)
        print("📊 TỔNG KẾT:")
        print("=" * 80)
        print(f"  • Tìm thấy {len(nodes_to_check)} node(s)")
        
        material_builders = [n for n in nodes_to_check if "MaterialBuilder" in n.type().name() and n.isNetwork()]
        material_nodes = [n for n in nodes_to_check if "Material" in n.type().name() and not n.isNetwork()]
        
        if material_builders:
            print(f"  • MaterialBuilder (network): {len(material_builders)} node(s)")
        if material_nodes:
            print(f"  • Material (single): {len(material_nodes)} node(s)")
        
        print()
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ LỖI: {e}")
        import traceback
        traceback.print_exc()


def find_all_material_builders():
    """Tìm tất cả Material Builder nodes trong scene"""
    print("=" * 80)
    print("TÌM TẤT CẢ MATERIAL BUILDER NODES")
    print("=" * 80)
    print()
    
    try:
        mat_context = hou.node("/mat")
        if mat_context is None:
            print("❌ Không tìm thấy /mat context!")
            return []
        
        material_builders = []
        for child in mat_context.children():
            type_name = child.type().name()
            if "MaterialBuilder" in type_name:
                material_builders.append(child)
        
        return material_builders
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return []


def create_test_material_builder_in_solaris():
    """Tạo Material Builder test trong Solaris"""
    print("=" * 80)
    print("TẠO MATERIAL BUILDER TRONG SOLARIS")
    print("=" * 80)
    print()
    
    try:
        # Kiểm tra /stage
        stage = hou.node("/stage")
        if not stage:
            print("❌ Không tìm thấy /stage context!")
            print("💡 Mở Solaris (Stage) pane để tạo /stage context")
            return None
        
        # Tạo Material Library
        matlib = stage.node("materiallibrary1")
        if not matlib:
            matlib = stage.createNode("materiallibrary", "materiallibrary1")
            print(f"✅ Đã tạo Material Library: {matlib.path()}")
        else:
            print(f"✅ Tìm thấy Material Library: {matlib.path()}")
        
        # Tạo Material Builder
        mat_builder = matlib.createNode("MaterialBuilder", "test_material")
        print(f"✅ Đã tạo Material Builder: {mat_builder.path()}")
        
        print()
        print("💡 Bây giờ chạy lại check_karma_material_builder() để kiểm tra!")
        
        return mat_builder
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    try:
        # Kiểm tra tất cả Material Builder nodes (cả /mat và /stage)
        check_karma_material_builder()
        
        # Nếu muốn kiểm tra node cụ thể, dùng:
        # check_karma_material_builder("/stage/materiallibrary1/my_material")
        # check_karma_material_builder("/mat/my_material")
        
        # Nếu muốn tạo test node trong Solaris:
        # create_test_material_builder_in_solaris()
        
    except ImportError:
        print("❌ Houdini Python module (hou) không tìm thấy!")
        print("💡 Chạy script này trong Houdini Python Shell")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
