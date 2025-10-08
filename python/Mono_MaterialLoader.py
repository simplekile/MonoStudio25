"""
Mock backend for Mono Material Loader
This provides placeholder functions when the real backend is not available.
"""

def create_usd_rs_materials_by_prefix(folder, matlib_node, prefix_map, udim, position_offset=(0.0, 0.0)):
    """Create Redshift materials from texture folder"""
    import os
    import hou
    
    print(f"Creating Redshift materials from {folder}")
    print(f"Material library: {matlib_node}")
    print(f"UDIM enabled: {udim}")
    
    # Get all texture files
    texture_files = []
    for f in os.listdir(folder):
        if f.lower().endswith(('.exr', '.jpg', '.jpeg', '.png', '.tif', '.tiff')):
            texture_files.append(f)
    
    if not texture_files:
        print("No texture files found!")
        return False
    
    # Group textures by material name (prefix)
    materials = {}
    for filename in texture_files:
        parsed = parse_texture_filename(filename)
        if parsed:
            prefix, ttype, ext, udim_token, variant = parsed
            if prefix not in materials:
                materials[prefix] = {}
            materials[prefix][ttype] = os.path.join(folder, filename)
    
    print(f"Found {len(materials)} materials: {list(materials.keys())}")
    
    # Create materials
    created_count = 0
    for mat_name, textures in materials.items():
        try:
            # Sanitize material name for Houdini
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', mat_name)
            safe_name = re.sub(r'_+', '_', safe_name).strip('_')
            if not safe_name or safe_name[0].isdigit():
                safe_name = 'mat_' + safe_name
            
            # Try different Redshift node types for Houdini 21
            mat_builder = None
            try:
                # Try MaterialX Material Builder first
                mat_builder = matlib_node.createNode("redshift::MaterialXBuilder", safe_name)
            except:
                try:
                    # Try standard Material Builder
                    mat_builder = matlib_node.createNode("redshift::MaterialBuilder", safe_name)
                except:
                    try:
                        # Try Material node directly
                        mat_builder = matlib_node.createNode("redshift::Material", safe_name)
                    except:
                        print(f"Error: No valid Redshift node type found for {safe_name}")
                        continue
            
            mat_builder.setPosition(matlib_node.position() + position_offset)
            
            # Create Material Output if we have a MaterialXBuilder
            if mat_builder.type().name() == "redshift::MaterialXBuilder":
                output = mat_builder.createNode("redshift::MaterialOutput")
                output.setPosition((0, 0))
                
                # Create Surface Shader
                surface = mat_builder.createNode("redshift::Material")
                surface.setPosition((-200, 0))
                output.setInput(0, surface, 0)
            else:
                # For direct Material node, we'll connect textures directly
                surface = mat_builder
            
            # Create texture nodes for each type
            for ttype, tex_path in textures.items():
                try:
                    if ttype == "basecolor":
                        # Base Color
                        tex_node = mat_builder.createNode("redshift::TextureSampler", f"{safe_name}_basecolor")
                        tex_node.parm("tex0").set(tex_path)
                        surface.setInput(0, tex_node, 0)  # Base Color
                        
                    elif ttype == "roughness":
                        # Roughness
                        tex_node = mat_builder.createNode("redshift::TextureSampler", f"{safe_name}_roughness")
                        tex_node.parm("tex0").set(tex_path)
                        surface.setInput(4, tex_node, 0)  # Roughness
                        
                    elif ttype == "metallic":
                        # Metallic
                        tex_node = mat_builder.createNode("redshift::TextureSampler", f"{safe_name}_metallic")
                        tex_node.parm("tex0").set(tex_path)
                        surface.setInput(5, tex_node, 0)  # Metallic
                        
                    elif ttype == "normal":
                        # Normal
                        tex_node = mat_builder.createNode("redshift::TextureSampler", f"{safe_name}_normal")
                        tex_node.parm("tex0").set(tex_path)
                        normal_map = mat_builder.createNode("redshift::BumpMap")
                        normal_map.setInput(0, tex_node, 0)
                        surface.setInput(6, normal_map, 0)  # Normal
                        
                    elif ttype == "height":
                        # Displacement
                        tex_node = mat_builder.createNode("redshift::TextureSampler", f"{safe_name}_height")
                        tex_node.parm("tex0").set(tex_path)
                        surface.setInput(7, tex_node, 0)  # Displacement
                        
                    elif ttype == "emissive":
                        # Emissive
                        tex_node = mat_builder.createNode("redshift::TextureSampler", f"{safe_name}_emissive")
                        tex_node.parm("tex0").set(tex_path)
                        surface.setInput(8, tex_node, 0)  # Emissive
                        
                    elif ttype == "opacity":
                        # Opacity
                        tex_node = mat_builder.createNode("redshift::TextureSampler", f"{safe_name}_opacity")
                        tex_node.parm("tex0").set(tex_path)
                        surface.setInput(9, tex_node, 0)  # Opacity
                        
                    elif ttype == "occlusion":
                        # AO
                        tex_node = mat_builder.createNode("redshift::TextureSampler", f"{safe_name}_ao")
                        tex_node.parm("tex0").set(tex_path)
                        # AO typically goes to a multiply node with base color
                        multiply = mat_builder.createNode("redshift::RSMultiply")
                        multiply.setInput(0, surface, 0)  # Base Color
                        multiply.setInput(1, tex_node, 0)  # AO
                        surface.setInput(0, multiply, 0)  # Replace base color with multiplied result
                        
                except Exception as tex_error:
                    print(f"Warning: Could not create texture node for {ttype}: {tex_error}")
                    continue
            
            # Layout nodes
            mat_builder.layoutChildren()
            created_count += 1
            print(f"Created material: {mat_name}")
            
        except Exception as e:
            print(f"Error creating material {mat_name}: {e}")
    
    print(f"Successfully created {created_count} Redshift materials!")
    return True

def create_karma_subnet_materials_by_prefix(folder, matlib_node, prefix_map, udim, position_offset=(0.0, 0.0)):
    """Create Karma materials from texture folder"""
    import os
    import hou
    
    print(f"Creating Karma materials from {folder}")
    print(f"Material library: {matlib_node}")
    print(f"UDIM enabled: {udim}")
    
    # Get all texture files
    texture_files = []
    for f in os.listdir(folder):
        if f.lower().endswith(('.exr', '.jpg', '.jpeg', '.png', '.tif', '.tiff')):
            texture_files.append(f)
    
    if not texture_files:
        print("No texture files found!")
        return False
    
    # Group textures by material name (prefix)
    materials = {}
    for filename in texture_files:
        parsed = parse_texture_filename(filename)
        if parsed:
            prefix, ttype, ext, udim_token, variant = parsed
            if prefix not in materials:
                materials[prefix] = {}
            materials[prefix][ttype] = os.path.join(folder, filename)
    
    print(f"Found {len(materials)} materials: {list(materials.keys())}")
    
    # Create materials
    created_count = 0
    for mat_name, textures in materials.items():
        try:
            # Sanitize material name for Houdini
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', mat_name)
            safe_name = re.sub(r'_+', '_', safe_name).strip('_')
            if not safe_name or safe_name[0].isdigit():
                safe_name = 'mat_' + safe_name
            
            # Try different Karma node types for Houdini 21
            mat_builder = None
            try:
                # Try MaterialX Material Builder first
                mat_builder = matlib_node.createNode("karma::MaterialXBuilder", safe_name)
            except:
                try:
                    # Try standard Material Builder
                    mat_builder = matlib_node.createNode("karma::MaterialBuilder", safe_name)
                except:
                    try:
                        # Try Material node directly
                        mat_builder = matlib_node.createNode("karma::Material", safe_name)
                    except:
                        print(f"Error: No valid Karma node type found for {safe_name}")
                        continue
            
            mat_builder.setPosition(matlib_node.position() + position_offset)
            
            # Create Material Output if we have a MaterialXBuilder
            if mat_builder.type().name() == "karma::MaterialXBuilder":
                output = mat_builder.createNode("karma::MaterialOutput")
                output.setPosition((0, 0))
                
                # Create Surface Shader
                surface = mat_builder.createNode("karma::Material")
                surface.setPosition((-200, 0))
                output.setInput(0, surface, 0)
            else:
                # For direct Material node, we'll connect textures directly
                surface = mat_builder
            
            # Create texture nodes for each type
            for ttype, tex_path in textures.items():
                try:
                    if ttype == "basecolor":
                        # Base Color
                        tex_node = mat_builder.createNode("karma::Texture", f"{safe_name}_basecolor")
                        tex_node.parm("filename").set(tex_path)
                        surface.setInput(0, tex_node, 0)  # Base Color
                        
                    elif ttype == "roughness":
                        # Roughness
                        tex_node = mat_builder.createNode("karma::Texture", f"{safe_name}_roughness")
                        tex_node.parm("filename").set(tex_path)
                        surface.setInput(1, tex_node, 0)  # Roughness
                        
                    elif ttype == "metallic":
                        # Metallic
                        tex_node = mat_builder.createNode("karma::Texture", f"{safe_name}_metallic")
                        tex_node.parm("filename").set(tex_path)
                        surface.setInput(2, tex_node, 0)  # Metallic
                        
                    elif ttype == "normal":
                        # Normal
                        tex_node = mat_builder.createNode("karma::Texture", f"{safe_name}_normal")
                        tex_node.parm("filename").set(tex_path)
                        normal_map = mat_builder.createNode("karma::NormalMap")
                        normal_map.setInput(0, tex_node, 0)
                        surface.setInput(3, normal_map, 0)  # Normal
                        
                    elif ttype == "height":
                        # Displacement
                        tex_node = mat_builder.createNode("karma::Texture", f"{safe_name}_height")
                        tex_node.parm("filename").set(tex_path)
                        surface.setInput(4, tex_node, 0)  # Displacement
                        
                    elif ttype == "emissive":
                        # Emissive
                        tex_node = mat_builder.createNode("karma::Texture", f"{safe_name}_emissive")
                        tex_node.parm("filename").set(tex_path)
                        surface.setInput(5, tex_node, 0)  # Emissive
                        
                    elif ttype == "opacity":
                        # Opacity
                        tex_node = mat_builder.createNode("karma::Texture", f"{safe_name}_opacity")
                        tex_node.parm("filename").set(tex_path)
                        surface.setInput(6, tex_node, 0)  # Opacity
                        
                    elif ttype == "occlusion":
                        # AO
                        tex_node = mat_builder.createNode("karma::Texture", f"{safe_name}_ao")
                        tex_node.parm("filename").set(tex_path)
                        # AO typically goes to a multiply node with base color
                        multiply = mat_builder.createNode("karma::Multiply")
                        multiply.setInput(0, surface, 0)  # Base Color
                        multiply.setInput(1, tex_node, 0)  # AO
                        surface.setInput(0, multiply, 0)  # Replace base color with multiplied result
                        
                except Exception as tex_error:
                    print(f"Warning: Could not create texture node for {ttype}: {tex_error}")
                    continue
            
            # Layout nodes
            mat_builder.layoutChildren()
            created_count += 1
            print(f"Created material: {mat_name}")
            
        except Exception as e:
            print(f"Error creating material {mat_name}: {e}")
    
    print(f"Successfully created {created_count} Karma materials!")
    return True

def parse_texture_filename(filename):
    """Parse texture filename to extract material name, type, and UDIM info"""
    import os
    import re
    
    name = os.path.basename(filename)
    stem, ext = os.path.splitext(name)
    lower = stem.lower()
    
    # UDIM detection
    udim = None
    # Check for <UDIM> or {UDIM} tokens
    for token in ["<udim>", "{udim}"]:
        if token in lower:
            udim = token
            break
    
    # Check for 4-digit UDIM numbers (1001-1999)
    if udim is None:
        udim_match = re.search(r'(\d{4})', stem)
        if udim_match:
            udim_num = int(udim_match.group(1))
            if 1001 <= udim_num <= 1999:
                udim = udim_match.group(1)
    
    # Remove UDIM tokens for type detection
    clean_stem = lower
    if udim:
        clean_stem = clean_stem.replace(udim.lower(), '')
    
    # Texture type mapping (more comprehensive)
    type_patterns = {
        'basecolor': ['basecolor', 'albedo', 'diffuse', 'color', 'col', 'base', 'diff'],
        'roughness': ['roughness', 'rough', 'rgh'],
        'metallic': ['metallic', 'metalness', 'metal', 'met'],
        'normal': ['normal', 'nrml', 'nrm', 'n'],
        'height': ['height', 'displacement', 'disp', 'h', 'd'],
        'specular': ['specular', 'spec', 's'],
        'emissive': ['emissive', 'emit', 'emission', 'e'],
        'opacity': ['opacity', 'alpha', 'transparency', 'trans', 'a'],
        'occlusion': ['ao', 'occlusion', 'ambient'],
        'gloss': ['gloss', 'glossiness'],
        'f0': ['f0', 'fresnel'],
        'coat': ['coat', 'clearcoat'],
        'coat_roughness': ['coatroughness', 'coat_rough', 'clearcoat_rough'],
    }
    
    # Find texture type
    detected_type = None
    for ttype, patterns in type_patterns.items():
        for pattern in patterns:
            if pattern in clean_stem:
                detected_type = ttype
                break
        if detected_type:
            break
    
    # Try suffix patterns (e.g., _bc, _r, _m, _n)
    if not detected_type:
        suffix_map = {
            'bc': 'basecolor',
            'r': 'roughness', 
            'rough': 'roughness',
            'm': 'metallic',
            'metal': 'metallic',
            'n': 'normal',
            'norm': 'normal',
            'h': 'height',
            'd': 'height',
            's': 'specular',
            'e': 'emissive',
            'emit': 'emissive',
            'a': 'opacity',
            'ao': 'occlusion',
            'g': 'gloss',
            'f0': 'f0',
            'c': 'coat',
            'cr': 'coat_roughness',
        }
        
        # Check last part after underscore or dash
        parts = re.split(r'[_-]', clean_stem)
        if parts:
            last_part = parts[-1]
            if last_part in suffix_map:
                detected_type = suffix_map[last_part]
    
    if not detected_type:
        return None
    
    # Extract material name (everything before the type indicator)
    material_name = stem
    if udim:
        material_name = material_name.replace(udim, '')
    
    # Remove type indicators from material name
    for ttype, patterns in type_patterns.items():
        for pattern in patterns:
            material_name = re.sub(r'[_-]?' + re.escape(pattern) + r'[_-]?', '', material_name, flags=re.IGNORECASE)
    
    # Clean up material name
    material_name = re.sub(r'[_-]+', '_', material_name).strip('_-')
    
    return (material_name, detected_type, ext.lstrip('.'), udim or '', '')
