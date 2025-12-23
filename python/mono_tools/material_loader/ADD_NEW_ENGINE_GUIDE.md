# Hướng dẫn thêm Render Engine mới vào Material Loader

Tài liệu này hướng dẫn cách thêm một render engine mới vào MonoStudio Material Loader mà không cần sửa đổi code core.

## Tổng quan

Material Loader sử dụng **Registry Pattern** để cho phép thêm engine mới một cách linh hoạt:
- Mỗi engine có file riêng (`material_loader_[engine].py`)
- Engine tự động đăng ký vào registry khi import
- UI tự động hiển thị tất cả engines đã đăng ký
- Input maps được quản lý riêng cho từng engine

## Các bước thêm Engine mới

### Bước 1: Tạo file Engine Implementation

Tạo file mới: `python/mono_tools/material_loader/material_loader_[engine_name].py`

**Template:**

```python
"""
[Engine Name] Material Creation for Mono Material Loader
Handles creation of [Engine] materials from texture folders.
"""

import os
from .material_loader_helpers import (
    parse_texture_filename,
    fallback_parse_texture_filename,
    ensure_udim_tag,
    connect_to_material_input,
    get_texture_files,
    sanitize_material_name,
)


def create_[engine]_materials_by_prefix(folder, matlib_node, prefix_map, udim, position_offset=(0.0, 0.0)):
    """
    Create [Engine] materials from texture folder.
    
    Args:
        folder: Path to folder containing textures
        matlib_node: Houdini node for material library
        prefix_map: Mapping of texture prefixes (currently unused)
        udim: Enable UDIM texture handling
        position_offset: Offset for material node positioning
    
    Returns:
        bool: True if materials were created successfully
    """
    try:
        import hou
    except ImportError:
        print("Error: Houdini Python module (hou) not available. Run this inside Houdini.")
        return False
    
    print(f"Creating [Engine] materials from {folder}")
    print(f"Material library: {matlib_node}")
    print(f"UDIM enabled: {udim}")
    
    # Get all texture files
    texture_files = get_texture_files(folder)
    
    if not texture_files:
        print("No texture files found!")
        return False
    
    # Try main parser first, fallback to simple parser
    parser = parse_texture_filename
    if not parser or not parser(texture_files[0]):
        parser = fallback_parse_texture_filename
    
    # Group textures by material name
    materials = {}
    unrecognized_textures = []  # Track unrecognized textures: (mat_name, ttype, tex_path, filename)
    
    for tex_file in texture_files:
        parsed = parser(tex_file)
        if parsed:
            prefix, ttype, ext, udim_token, variant = parsed
            mat_name = sanitize_material_name(prefix)
            
            if mat_name not in materials:
                materials[mat_name] = {}
            
            tex_path = os.path.join(folder, tex_file)
            if udim and udim_token:
                tex_path = ensure_udim_tag(tex_path)
            
            materials[mat_name][ttype] = tex_path
        else:
            # Texture couldn't be parsed - track for dialog
            name_without_ext = os.path.splitext(tex_file)[0]
            parts = name_without_ext.replace("-", "_").split("_")
            if len(parts) > 1:
                prefix = "_".join(parts[:-1])
                ttype = parts[-1]
            else:
                prefix = "unrecognized"
                ttype = name_without_ext
            
            tex_path = os.path.join(folder, tex_file)
            if udim:
                tex_path = ensure_udim_tag(tex_path)
            
            unrecognized_textures.append((prefix, ttype, tex_path, tex_file))
    
    # Show dialog for unrecognized textures if any
    texture_choices = {}
    if unrecognized_textures:
        try:
            import hou
            from .material_input_maps import get_available_inputs_for_engine
            
            # Import Qt and dialog (optional)
            try:
                from .qt import QtWidgets
            except:
                try:
                    from mono_tools.qt import QtWidgets
                except:
                    QtWidgets = None
            
            try:
                from .unrecognized_textures_dialog import UnrecognizedTexturesDialog
            except ImportError:
                try:
                    from mono_tools.material_loader.unrecognized_textures_dialog import UnrecognizedTexturesDialog
                except ImportError:
                    UnrecognizedTexturesDialog = None
            
            # Get available inputs for this engine
            available_inputs = get_available_inputs_for_engine("[engine_name]")
            
            # Show dialog if available
            if QtWidgets and UnrecognizedTexturesDialog:
                dialog = UnrecognizedTexturesDialog(
                    parent=hou.qt.mainWindow(),
                    unrecognized_textures=unrecognized_textures,
                    available_inputs=available_inputs
                )
                
                if dialog.exec() == QtWidgets.QDialog.Accepted:
                    texture_choices = dialog.get_choices()
                    print(f"✓ User configured {len(texture_choices)} unrecognized texture(s)")
                else:
                    print("⚠️  User cancelled unrecognized textures dialog")
        except Exception as e:
            print(f"⚠️  Could not show unrecognized textures dialog: {e}")
    
    if not materials:
        print("No materials found!")
        return False
    
    print(f"Found {len(materials)} materials: {list(materials.keys())}")
    
    # Create materials
    for mat_name, textures in materials.items():
        # TODO: Implement material creation logic here
        # Example:
        # 1. Create material node in matlib_node
        # 2. Create texture nodes for each texture type
        # 3. Connect textures to material inputs using connect_to_material_input()
        #    Remember to pass engine="[engine_name]" parameter!
        pass
    
    print(f"Successfully created {len(materials)} [Engine] materials!")
    return True
```

### Bước 2: Tạo Input Map cho Engine

Thêm input map vào `material_input_maps.py` hoặc tạo trong file engine của bạn:

```python
# Trong material_input_maps.py hoặc file engine của bạn

[ENGINE_NAME]_INPUT_MAP = {
    "basecolor": {"input_name": "[engine_specific_name]", "index": 0, "aliases": ["color", "albedo", "diffuse"]},
    "roughness": {"input_name": "[engine_specific_name]", "index": 1, "aliases": ["rough", "specular_roughness"]},
    "metallic": {"input_name": "[engine_specific_name]", "index": 2, "aliases": ["metalness", "metallicness"]},
    "normal": {"input_name": "[engine_specific_name]", "index": 3, "aliases": ["normalmap", "bump"]},
    "displacement": {"input_name": "[engine_specific_name]", "index": 4, "aliases": ["height"]},
    "emission": {"input_name": "[engine_specific_name]", "index": 5, "aliases": ["emissive", "emissioncolor"]},
    "opacity": {"input_name": "[engine_specific_name]", "index": 6, "aliases": ["alpha", "transparency"]},
    "ao": {"input_name": "[engine_specific_name]", "index": 7, "aliases": ["occlusion", "ambient_occlusion"]},
    # Thêm các texture types khác nếu cần
}
```

### Bước 3: Đăng ký Engine và Input Map

Thêm vào cuối file engine của bạn:

```python
# Auto-register engine
from .material_loader_registry import register_engine
from .material_input_maps import register_input_map

# Register engine
register_engine("[engine_name]", create_[engine]_materials_by_prefix, "[Display Name]")

# Register input map
register_input_map("[engine_name]", [ENGINE_NAME]_INPUT_MAP)
```

**Hoặc** nếu muốn đăng ký trong `material_loader_registry.py`:

```python
# Trong material_loader_registry.py, thêm vào _auto_register_engines():

try:
    from .material_loader_[engine] import create_[engine]_materials_by_prefix
    register_engine("[engine_name]", create_[engine]_materials_by_prefix, "[Display Name]")
except ImportError:
    pass
```

## Ví dụ: Thêm Arnold Engine

### File: `material_loader_arnold.py`

```python
"""
Arnold Material Creation for Mono Material Loader
Handles creation of Arnold Standard Surface materials from texture folders.
"""

import os
import hou
from .material_loader_helpers import (
    parse_texture_filename,
    fallback_parse_texture_filename,
    ensure_udim_tag,
    connect_to_material_input,
    get_texture_files,
    sanitize_material_name,
)

# Arnold Standard Surface input map
ARNOLD_INPUT_MAP = {
    "basecolor": {"input_name": "base_color", "index": 0, "aliases": ["color", "albedo", "diffuse"]},
    "roughness": {"input_name": "specular_roughness", "index": 1, "aliases": ["rough", "specular_roughness"]},
    "metallic": {"input_name": "metalness", "index": 2, "aliases": ["metalness", "metallicness"]},
    "normal": {"input_name": "normal", "index": 3, "aliases": ["normalmap", "bump"]},
    "displacement": {"input_name": "height", "index": 4, "aliases": ["displacement", "height"]},
    "emission": {"input_name": "emission", "index": 5, "aliases": ["emissive", "emissioncolor"]},
    "opacity": {"input_name": "opacity", "index": 6, "aliases": ["alpha", "transparency"]},
    "ao": {"input_name": "ao", "index": 7, "aliases": ["occlusion", "ambient_occlusion"]},
}


def create_arnold_materials_by_prefix(folder, matlib_node, prefix_map, udim, position_offset=(0.0, 0.0)):
    """
    Create Arnold Standard Surface materials from texture folder.
    """
    try:
        import hou
    except ImportError:
        print("Error: Houdini Python module (hou) not available. Run this inside Houdini.")
        return False
    
    print(f"Creating Arnold materials from {folder}")
    print(f"Material library: {matlib_node}")
    print(f"UDIM enabled: {udim}")
    
    # Get all texture files
    texture_files = get_texture_files(folder)
    
    if not texture_files:
        print("No texture files found!")
        return False
    
    # Parse textures and group by material
    parser = parse_texture_filename or fallback_parse_texture_filename
    materials = {}
    
    for tex_file in texture_files:
        parsed = parser(tex_file)
        if not parsed:
            continue
        
        prefix, ttype, ext, udim_token, variant = parsed
        mat_name = sanitize_material_name(prefix)
        
        if mat_name not in materials:
            materials[mat_name] = {}
        
        materials[mat_name][ttype] = {
            "path": os.path.join(folder, tex_file),
            "udim": udim_token is not None,
        }
    
    if not materials:
        print("No materials found!")
        return False
    
    print(f"Found {len(materials)} materials: {list(materials.keys())}")
    
    # Create materials
    x_offset = position_offset[0]
    y_offset = position_offset[1]
    
    for idx, (mat_name, textures) in enumerate(materials.items()):
        # Create Arnold Standard Surface material
        mat_node = matlib_node.createNode("arnold_materialbuilder", mat_name)
        mat_node.setPosition([x_offset, y_offset - idx * 2])
        
        # Find the Standard Surface node inside the builder
        surface = None
        for child in mat_node.children():
            if "standard_surface" in child.type().name().lower():
                surface = child
                break
        
        if not surface:
            print(f"  ✗ Could not find Standard Surface in {mat_name}")
            continue
        
        print(f"  ✓ Created Arnold material: {mat_name}")
        
        # Create and connect textures
        for ttype, tex_info in textures.items():
            tex_path = ensure_udim_tag(tex_info["path"]) if tex_info["udim"] and udim else tex_info["path"]
            
            # Create texture node (Arnold uses "arnold::image" or "arnold_image")
            tex_node = mat_node.createNode("arnold::image", f"{mat_name}_{ttype}")
            if tex_node:
                # Set file path
                file_parm = tex_node.parm("filename")
                if file_parm:
                    file_parm.set(tex_path)
                
                # Enable UDIM if needed
                if udim and tex_info["udim"]:
                    udim_parm = tex_node.parm("udim_enable") or tex_node.parm("udim")
                    if udim_parm:
                        udim_parm.set(1)
                
                # Connect to material input (IMPORTANT: pass engine="arnold")
                connect_to_material_input(surface, ttype, tex_node, 0, engine="arnold")
                print(f"    ✓ Connected {ttype} texture")
    
    print(f"Successfully created {len(materials)} Arnold materials!")
    return True


# Auto-register engine
from .material_loader_registry import register_engine
from .material_input_maps import register_input_map

register_engine("arnold", create_arnold_materials_by_prefix, "Arnold")
register_input_map("arnold", ARNOLD_INPUT_MAP)
```

## Hỗ trợ Unrecognized Textures Dialog

Tính năng **Unrecognized Textures Dialog** tự động hoạt động với tất cả engines nếu bạn:

1. **Track unrecognized textures** trong parsing loop (như template ở trên)
2. **Import dialog và Qt** (optional imports với try/except)
3. **Get available inputs** từ input map: `get_available_inputs_for_engine("[engine_name]")`
4. **Show dialog** và lưu user choices vào `texture_choices` dict
5. **Xử lý user choices** khi tạo materials:
   - `"skip"`: Bỏ qua texture
   - `"unconnected"`: Tạo texture node nhưng không connect
   - `"connect"`: Tạo texture node và connect với input user chọn

**Ví dụ xử lý unrecognized texture trong material creation loop:**

```python
# Khi gặp texture type không có trong input map
texture_key = f"{mat_name}::{ttype}"
choice = texture_choices.get(texture_key)

if choice and choice["action"] == "skip":
    continue  # Skip texture
elif choice and choice["action"] == "connect":
    input_name = choice.get("input")
    if input_name:
        # Create texture node and connect to input_name
        # ... your engine-specific code ...
elif choice and choice["action"] == "unconnected":
    # Create texture node but don't connect
    # ... your engine-specific code ...
```

**Lưu ý**: Tính năng này tự động hoạt động nếu bạn follow template. Dialog sẽ:
- Tự động lấy available inputs từ input map của engine
- Hiển thị dialog với inputs phù hợp cho engine đó
- Xử lý theo user choice một cách nhất quán

## Checklist khi thêm Engine mới

- [ ] Tạo file `material_loader_[engine].py` với function `create_[engine]_materials_by_prefix()`
- [ ] Tạo input map cho engine (trong file engine hoặc `material_input_maps.py`)
- [ ] Đăng ký engine với `register_engine()`
- [ ] Đăng ký input map với `register_input_map()`
- [ ] Sử dụng `connect_to_material_input()` với parameter `engine="[engine_name]"` khi connect textures
- [ ] **Implement unrecognized textures tracking và dialog** (xem template ở trên)
- [ ] **Xử lý user choices** cho unrecognized textures trong material creation loop
- [ ] Test engine trong Houdini
- [ ] Kiểm tra engine xuất hiện trong UI Material Loader
- [ ] Test unrecognized textures dialog với engine mới

## Lưu ý quan trọng

1. **Function signature**: Function `create_[engine]_materials_by_prefix()` phải có signature chính xác:
   ```python
   (folder, matlib_node, prefix_map, udim, position_offset=(0.0, 0.0))
   ```

2. **Engine name**: Sử dụng lowercase, không có spaces (e.g., "arnold", "mantra", "vray")

3. **Input map**: Mỗi texture type phải map đến đúng input name và index của engine đó

4. **connect_to_material_input()**: Luôn truyền `engine="[engine_name]"` để sử dụng đúng input map

5. **Auto-registration**: Engine sẽ tự động xuất hiện trong UI sau khi đăng ký, không cần sửa `material_loader.py`

## Troubleshooting

### Engine không xuất hiện trong UI
- Kiểm tra engine đã được import chưa (import statement trong `material_loader_registry.py`)
- Kiểm tra `register_engine()` đã được gọi chưa
- Kiểm tra không có lỗi import khi load module

### Textures không connect đúng
- Kiểm tra input map có đúng input names của engine không
- Kiểm tra đã truyền `engine="[engine_name]"` vào `connect_to_material_input()` chưa
- Kiểm tra input indices có đúng không

### Material node không tạo được
- Kiểm tra node type name có đúng không (dùng `hou.node.createNode()`)
- Kiểm tra material library node có đúng type không
- Kiểm tra Houdini có plugin của engine đó không

## Tài liệu tham khảo

- Xem `material_loader_karma.py` và `material_loader_redshift.py` để tham khảo implementation
- Xem `material_input_maps.py` để tham khảo input map structure
- Xem `material_loader_registry.py` để hiểu registry system

