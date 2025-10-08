"""
Mock backend for Mono Material Loader
This provides placeholder functions when the real backend is not available.
"""

def create_usd_rs_materials_by_prefix(folder, matlib_node, prefix_map, udim, position_offset=(0.0, 0.0)):
    """Create Redshift materials from texture folder"""
    import os
    import re
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
            
            # Create rs_usd_material_builder (correct node type from original script)
            mat_builder = matlib_node.createNode("rs_usd_material_builder", safe_name)
            
            # Convert position_offset tuple to Vector2 and add to material library position
            lib_pos = matlib_node.position()
            offset_x, offset_y = position_offset
            new_pos = (lib_pos[0] + offset_x, lib_pos[1] + offset_y)
            mat_builder.setPosition(new_pos)
            
            # Find existing StandardMaterial1 and redshift_usd_material1 nodes
            rs_mat = None
            usd_mat = None
            
            # Look for StandardMaterial1
            for child in mat_builder.children():
                if child.name() == "StandardMaterial1" or "standardmaterial" in child.name().lower():
                    rs_mat = child
                    break
            
            # Look for redshift_usd_material1
            for child in mat_builder.children():
                if child.name() == "redshift_usd_material1" or "redshift_usd_material" in child.name().lower():
                    usd_mat = child
                    break
            
            if not rs_mat or not usd_mat:
                print(f"Warning: Could not find StandardMaterial1 or redshift_usd_material1 in {safe_name}")
                continue
            
            # Create texture nodes for each type using original script logic
            base_x, base_y = mat_builder.position()
            
            for idx, (ttype, tex_path) in enumerate(sorted(textures.items())):
                try:
                    t_upper = ttype.upper()
                    
                    # Displacement handling
                    if t_upper == "DISPLACEMENT":
                        disp_node = mat_builder.node("RS_Displacement")
                        if disp_node is None:
                            disp_node = mat_builder.createNode("redshift::Displacement", "RS_Displacement")
                            
                        disp_node.setPosition((base_x + 1.5, base_y - 1.0 - idx))
                        
                        # Set texture path
                        tex_parm = disp_node.parm("tex0") or disp_node.parm("tex")
                        if tex_parm:
                            tex_parm.set(tex_path)
                        
                        # Set colorspace to Raw for displacement
                        cs_parm = disp_node.parm("tex0_colorSpace") or disp_node.parm("tex_colorSpace")
                        if cs_parm:
                            cs_parm.set("Utility - Raw")
                            
                        if udim:
                            udim_parm = disp_node.parm("udim_enable")
                            if udim_parm:
                                udim_parm.set(1)
                        
                        # Connect to USD material displacement input
                        disp_port_idx = None
                        for i, nm in enumerate(usd_mat.inputNames() or []):
                            if nm and "displacement" in nm.lower():
                                disp_port_idx = i
                                break
                        if disp_port_idx is not None:
                            usd_mat.setInput(disp_port_idx, disp_node, 0)
                        continue

                    # Normal map handling
                    if t_upper in {"NRM", "NORMAL", "NORMALGL", "NORMALMAP", "COATNORMAL"}:
                        nrm = mat_builder.node(f"NormalMap_{ttype}")
                        if nrm is None:
                            nrm = mat_builder.createNode("redshift::NormalMap", f"NormalMap_{ttype}")
                            
                        nrm.setPosition((base_x + 1.0, base_y - 1.0 - idx))
                        
                        # Set texture path
                        tex_parm = nrm.parm("tex0")
                        if tex_parm:
                            tex_parm.set(tex_path)
                        
                        # Set colorspace to Raw for normal maps
                        cs_parm = nrm.parm("tex0_colorSpace")
                        if cs_parm:
                            cs_parm.set("Utility - Raw")
                            
                        if udim:
                            udim_parm = nrm.parm("udim_enable")
                            if udim_parm:
                                udim_parm.set(1)
                        
                        # Connect to bump_input
                        bump_port_idx = None
                        for i, nm in enumerate(rs_mat.inputNames() or []):
                            if nm and "bump" in nm.lower():
                                bump_port_idx = i
                                break
                        if bump_port_idx is not None:
                            rs_mat.setInput(bump_port_idx, nrm, 0)
                        continue

                    # Regular texture sampler
                    ts = mat_builder.node(f"TS_{ttype}")
                    if ts is None:
                        ts = mat_builder.createNode("redshift::TextureSampler", f"TS_{ttype}")
                        
                    ts.setPosition((base_x + 1.0, base_y - 1.0 - idx))
                    
                    # Set texture path
                    tex_parm = ts.parm("tex0")
                    if tex_parm:
                        tex_parm.set(tex_path)

                    # Set colorspace based on texture type
                    cs_parm = ts.parm("tex0_colorSpace")
                    if cs_parm:
                        # Non-color textures should use Raw
                        NONCOLOR_FORCE_RAW = {
                            "NRM", "NORMAL", "NORMALGL", "NORMALMAP", "COATNORMAL",
                            "ROUGHNESS", "COATROUGHNESS",
                            "METALNESS", "METAL", "METALNESSMAP",
                            "OPACITY", "ALPHA",
                            "EMISSIVE", "DISPLACEMENT",
                            "TRANSLUCENCY", "SCATTERING"
                        }
                        if t_upper in NONCOLOR_FORCE_RAW:
                            cs_parm.set("Utility - Raw")
                        # else: leave as Auto for color textures

                    if udim:
                        udim_parm = ts.parm("udim_enable")
                        if udim_parm:
                            udim_parm.set(1)

                    # Map to appropriate input based on texture type
                    port_mapping = {
                        "BASECOLOR": "base_color",
                        "COLOR": "base_color", 
                        "ALBEDO": "base_color",
                        "DIFFUSE": "base_color",
                        "ROUGHNESS": "refl_roughness",
                        "METALNESS": "metalness",
                        "METALLIC": "metalness",
                        "EMISSION": "emission_color",
                        "EMISSIVE": "emission_color",
                        "OPACITY": "opacity_color",
                        "ALPHA": "opacity_color",
                    }
                    
                    port_name = port_mapping.get(t_upper)
                    if port_name:
                        # Find the input port
                        port_idx = None
                        for i, nm in enumerate(rs_mat.inputNames() or []):
                            if nm and port_name in nm.lower():
                                port_idx = i
                                break
                        if port_idx is not None:
                            rs_mat.setInput(port_idx, ts, 0)
                        else:
                            print(f"Warning: Could not find input port '{port_name}' for texture '{ttype}'")
                    else:
                        print(f"Warning: No mapping found for texture type '{ttype}'")
                        
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
    import re
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
            
            # Convert position_offset tuple to Vector2 and add to material library position
            lib_pos = matlib_node.position()
            offset_x, offset_y = position_offset
            new_pos = (lib_pos[0] + offset_x, lib_pos[1] + offset_y)
            mat_builder.setPosition(new_pos)
            
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
    """
    Parse texture filename to extract material name, type, UDIM, and colorspace info.
    Based on the original script's parser with improved detection.
    """
    import os
    import re
    
    name = os.path.basename(filename)
    stem, ext = os.path.splitext(name)
    if not ext:
        return None

    parts = stem.split('.')
    if len(parts) < 2:
        return None

    udim = parts[-1] if parts[-1].isdigit() and len(parts[-1]) == 4 else None
    if not udim:
        return None

    main_part = parts[-2]
    raw_colorspace_name = None

    # Extract colorspace from " - <ColorSpaceName>" pattern
    if ' - ' in main_part:
        left, right = main_part.split(' - ', 1)
        raw_colorspace_name = right.strip()  # ACEScg / Raw / sRGB ...
        main_part = left

    # Remove suffix colorspace family if present (ACES/Utility/Raw/sRGB)
    tokens = main_part.split('_')
    LOWERS = {"aces", "utility", "raw", "srgb"}
    if len(tokens) > 1 and tokens[-1].lower() in LOWERS:
        tokens = tokens[:-1]

    texture_type = tokens[-1] if tokens else ""
    prefix = '_'.join(tokens[:-1]) if len(tokens) > 1 else ""

    if not texture_type:
        return None
    
    return prefix, texture_type, udim, ext, raw_colorspace_name
