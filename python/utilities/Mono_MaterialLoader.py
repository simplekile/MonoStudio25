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
            # parse_texture_filename returns: (prefix, texture_type, ext, udim_token, variant)
            # Unpack correctly
            prefix, ttype, ext, udim_token, variant = parsed
            if prefix not in materials:
                materials[prefix] = {}
            # Convert UDIM numbers to <UDIM> tag if UDIM is enabled
            tex_path = os.path.join(folder, filename)
            if udim and udim_token:
                tex_path = ensure_udim_tag(tex_path)
            
            materials[prefix][ttype] = tex_path
    
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
                    
                    # Displacement handling (for both DISPLACEMENT and HEIGHT)
                    if t_upper in ["DISPLACEMENT", "HEIGHT"]:
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
                        "NORMAL": "bump_input",
                        "NRM": "bump_input",
                        "NORMALMAP": "bump_input",
                        "NORMALGL": "bump_input",
                        "COATNORMAL": "coat_bump_input",
                    }
                    
                    port_name = port_mapping.get(t_upper)
                    
                    # Fallback mapping for unknown texture types
                    if not port_name:
                        # Skip Height/Displacement as they're handled separately
                        if any(x in t_upper for x in ['HEIGHT', 'DISPLACE', 'DISP']):
                            print(f"Info: Skipping '{ttype}' - handled as displacement")
                            continue
                        elif any(x in t_upper for x in ['NORMAL', 'NRM', 'BUMP']):
                            port_name = "bump_input"
                        elif any(x in t_upper for x in ['COLOR', 'ALBEDO', 'DIFFUSE', 'BASE']):
                            port_name = "base_color"
                        elif any(x in t_upper for x in ['ROUGH', 'RGH']):
                            port_name = "refl_roughness"
                        elif any(x in t_upper for x in ['METAL', 'METALLIC']):
                            port_name = "metalness"
                        elif any(x in t_upper for x in ['EMISS', 'GLOW']):
                            port_name = "emission_color"
                        elif any(x in t_upper for x in ['OPAC', 'ALPHA', 'TRANSPARENCY']):
                            port_name = "opacity_color"
                        else:
                            # Default fallback - try to map to base_color
                            port_name = "base_color"
                            print(f"Info: Using fallback mapping for '{ttype}' -> base_color")
                    
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

def _connect_to_material_input(surface_node, input_name, source_node, output_index):
    """Helper function to connect texture to material input by name or index"""
    try:
        # Try to find input by name
        input_names = surface_node.inputNames()
        if input_names:
            for i, name in enumerate(input_names):
                if name and input_name.lower() in name.lower():
                    surface_node.setInput(i, source_node, output_index)
                    return True
        
        # Fallback: try common input indices based on input name
        input_map = {
            "basecolor": 0, "color": 0, "albedo": 0, "diffuse": 0,
            "roughness": 1, "rough": 1,
            "metallic": 2, "metalness": 2,
            "normal": 3, "normalmap": 3,
            "displacement": 4, "height": 4,
            "emission": 5, "emissive": 5,
            "opacity": 6, "alpha": 6,
            "ao": 7, "occlusion": 7,
        }
        
        if input_name.lower() in input_map:
            idx = input_map[input_name.lower()]
            if idx < len(surface_node.inputs() or []):
                surface_node.setInput(idx, source_node, output_index)
                return True
        
        # Last resort: try to set as parameter if available
        parm = surface_node.parm(input_name) or surface_node.parm(input_name.lower())
        if parm:
            parm.set(source_node)
            return True
            
    except Exception as e:
        pass
    return False

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
            # parse_texture_filename returns: (prefix, texture_type, ext, udim_token, variant)
            # Unpack correctly
            prefix, ttype, ext, udim_token, variant = parsed
            if prefix not in materials:
                materials[prefix] = {}
            # Convert UDIM numbers to <UDIM> tag if UDIM is enabled
            tex_path = os.path.join(folder, filename)
            if udim and udim_token:
                tex_path = ensure_udim_tag(tex_path)
            
            materials[prefix][ttype] = tex_path
    
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
            node_type_errors = []
            
            # List of possible node types to try (most common first)
            # MaterialBuilder is a network node (can contain child nodes)
            # Material is a single node (cannot contain child nodes, only parameters)
            node_types_to_try = [
                "MaterialBuilder",  # Standard Material Builder (network node - PREFERRED)
                "karma::MaterialBuilder",  # With namespace (network node)
                "Material::2.0",  # Material node version 2.0 (single node - parameters only)
                "Material",  # Material node (single node - parameters only)
                "subnet",  # Fallback: create subnet and add material inside
            ]
            
            for node_type in node_types_to_try:
                try:
                    mat_builder = matlib_node.createNode(node_type, safe_name)
                    print(f"✓ Created {node_type} node: {safe_name}")
                    break
                except Exception as e:
                    node_type_errors.append(f"{node_type}: {str(e)}")
                    continue
            
            if mat_builder is None:
                print(f"Error: No valid Karma node type found for {safe_name}")
                print(f"Tried node types: {', '.join(node_types_to_try)}")
                print(f"Errors: {'; '.join(node_type_errors)}")
                continue
            
            # Convert position_offset tuple to Vector2 and add to material library position
            lib_pos = matlib_node.position()
            offset_x, offset_y = position_offset
            new_pos = (lib_pos[0] + offset_x, lib_pos[1] + offset_y)
            mat_builder.setPosition(new_pos)
            
            # Get node type name for logic branching
            node_type_name = mat_builder.type().name()
            is_network = mat_builder.isNetwork()
            
            print(f"Created node type: {node_type_name}, isNetwork: {is_network}")
            
            # For MaterialBuilder or subnet (network nodes), we can create child nodes inside
            if is_network and (node_type_name == "MaterialBuilder" or node_type_name == "subnet"):
                # Create a Material node inside the builder/subnet
                try:
                    surface = mat_builder.createNode("Material", "material1")
                    print(f"Created Material node inside {node_type_name}")
                except:
                    try:
                        surface = mat_builder.createNode("Material::2.0", "material1")
                        print(f"Created Material::2.0 node inside {node_type_name}")
                    except Exception as e:
                        print(f"Warning: Could not create Material node inside {node_type_name}: {e}")
                        surface = mat_builder
            elif "Material" in node_type_name and not is_network:
                # For direct Material node (NOT a network), set texture paths directly to parameters
                # Material node has parameters like basecolor, roughness, etc.
                surface = mat_builder
                print(f"Using Material node directly (parameter-based, not network)")
            else:
                # Fallback: try to find or create a material node
                surface = mat_builder
                print(f"Fallback: using {node_type_name} as surface")
            
            # Check if we're working with a network node (can create child nodes) or single node (parameters only)
            if is_network:
                # Create texture nodes for each type (network node approach)
                # Try different texture node types
                texture_node_types = ["Texture", "karma::Texture", "vop::Texture"]
                
                def create_texture_node(name_suffix):
                    """Helper to create texture node with fallback types"""
                    for tex_type in texture_node_types:
                        try:
                            return mat_builder.createNode(tex_type, f"{safe_name}_{name_suffix}")
                        except:
                            continue
                    return None
            else:
                # For single Material node, we'll set parameters directly
                def create_texture_node(name_suffix):
                    """Not needed for parameter-based approach"""
                    return None
            
            for ttype, tex_path in textures.items():
                try:
                    # If Material node is NOT a network, set texture paths directly to parameters
                    if not is_network and "Material" in node_type_name:
                        # Direct parameter setting for Material node
                        param_names = {
                            "basecolor": ["basecolor", "base_color", "color", "albedo", "diffuse"],
                            "roughness": ["roughness", "rough"],
                            "metallic": ["metallic", "metalness", "metallicness"],
                            "normal": ["normal", "normalmap"],
                            "displacement": ["displacement", "height"],
                            "emission": ["emission", "emissive"],
                            "opacity": ["opacity", "alpha", "transparency"],
                            "ao": ["ao", "occlusion", "ambient_occlusion"]
                        }
                        
                        # Find matching parameter name
                        param_set = False
                        for param_group, aliases in param_names.items():
                            if ttype.lower() in aliases:
                                for alias in aliases:
                                    parm = surface.parm(alias) or surface.parm(f"{alias}_map") or surface.parm(f"{alias}_texture")
                                    if parm:
                                        parm.set(tex_path)
                                        if udim:
                                            # Try to enable UDIM
                                            udim_parm = surface.parm(f"{alias}_udim") or surface.parm(f"{alias}_udim_enable")
                                            if udim_parm:
                                                udim_parm.set(1)
                                        print(f"  Set {alias} parameter: {tex_path}")
                                        param_set = True
                                        break
                                if param_set:
                                    break
                        
                        if not param_set:
                            print(f"  Warning: Could not find parameter for texture type: {ttype}")
                        continue
                    
                    # Network node approach - create texture nodes
                    # Try to set texture using parameter names (more reliable than input indices)
                    if ttype == "basecolor" or ttype == "color" or ttype == "albedo" or ttype == "diffuse":
                        # Base Color - try different parameter names
                        tex_node = create_texture_node("basecolor")
                        if tex_node:
                            if tex_node.parm("filename"):
                                tex_node.parm("filename").set(tex_path)
                            elif tex_node.parm("file"):
                                tex_node.parm("file").set(tex_path)
                            if udim:
                                udim_parm = tex_node.parm("udim_enable") or tex_node.parm("udim")
                                if udim_parm:
                                    udim_parm.set(1)
                            # Try to connect to basecolor input
                            _connect_to_material_input(surface, "basecolor", tex_node, 0)
                        
                    elif ttype == "roughness" or ttype == "rough":
                        # Roughness
                        tex_node = create_texture_node("roughness")
                        if tex_node:
                            if tex_node.parm("filename"):
                                tex_node.parm("filename").set(tex_path)
                            elif tex_node.parm("file"):
                                tex_node.parm("file").set(tex_path)
                            if udim:
                                udim_parm = tex_node.parm("udim_enable") or tex_node.parm("udim")
                                if udim_parm:
                                    udim_parm.set(1)
                            _connect_to_material_input(surface, "roughness", tex_node, 0)
                        
                    elif ttype == "metallic" or ttype == "metallicness" or ttype == "metalness":
                        # Metallic
                        tex_node = create_texture_node("metallic")
                        if tex_node:
                            if tex_node.parm("filename"):
                                tex_node.parm("filename").set(tex_path)
                            elif tex_node.parm("file"):
                                tex_node.parm("file").set(tex_path)
                            if udim:
                                udim_parm = tex_node.parm("udim_enable") or tex_node.parm("udim")
                                if udim_parm:
                                    udim_parm.set(1)
                            _connect_to_material_input(surface, "metallic", tex_node, 0)
                        
                    elif ttype == "normal" or ttype == "normalmap":
                        # Normal
                        tex_node = create_texture_node("normal")
                        if tex_node:
                            if tex_node.parm("filename"):
                                tex_node.parm("filename").set(tex_path)
                            elif tex_node.parm("file"):
                                tex_node.parm("file").set(tex_path)
                            if udim:
                                udim_parm = tex_node.parm("udim_enable") or tex_node.parm("udim")
                                if udim_parm:
                                    udim_parm.set(1)
                            # Try to create normal map node
                            try:
                                normal_map = mat_builder.createNode("NormalMap", f"{safe_name}_normalmap")
                                if normal_map:
                                    normal_map.setInput(0, tex_node, 0)
                                    _connect_to_material_input(surface, "normal", normal_map, 0)
                                else:
                                    _connect_to_material_input(surface, "normal", tex_node, 0)
                            except:
                                _connect_to_material_input(surface, "normal", tex_node, 0)
                        
                    elif ttype == "height" or ttype == "displacement":
                        # Displacement/Height
                        tex_node = create_texture_node("height")
                        if tex_node:
                            if tex_node.parm("filename"):
                                tex_node.parm("filename").set(tex_path)
                            elif tex_node.parm("file"):
                                tex_node.parm("file").set(tex_path)
                            if udim:
                                udim_parm = tex_node.parm("udim_enable") or tex_node.parm("udim")
                                if udim_parm:
                                    udim_parm.set(1)
                            _connect_to_material_input(surface, "displacement", tex_node, 0)
                        
                    elif ttype == "emissive" or ttype == "emission":
                        # Emissive
                        tex_node = create_texture_node("emissive")
                        if tex_node:
                            if tex_node.parm("filename"):
                                tex_node.parm("filename").set(tex_path)
                            elif tex_node.parm("file"):
                                tex_node.parm("file").set(tex_path)
                            if udim:
                                udim_parm = tex_node.parm("udim_enable") or tex_node.parm("udim")
                                if udim_parm:
                                    udim_parm.set(1)
                            _connect_to_material_input(surface, "emission", tex_node, 0)
                        
                    elif ttype == "opacity" or ttype == "alpha" or ttype == "transparency":
                        # Opacity
                        tex_node = create_texture_node("opacity")
                        if tex_node:
                            if tex_node.parm("filename"):
                                tex_node.parm("filename").set(tex_path)
                            elif tex_node.parm("file"):
                                tex_node.parm("file").set(tex_path)
                            if udim:
                                udim_parm = tex_node.parm("udim_enable") or tex_node.parm("udim")
                                if udim_parm:
                                    udim_parm.set(1)
                            _connect_to_material_input(surface, "opacity", tex_node, 0)
                        
                    elif ttype == "occlusion" or ttype == "ao":
                        # AO - typically multiply with base color
                        tex_node = create_texture_node("ao")
                        if tex_node:
                            if tex_node.parm("filename"):
                                tex_node.parm("filename").set(tex_path)
                            elif tex_node.parm("file"):
                                tex_node.parm("file").set(tex_path)
                            if udim:
                                udim_parm = tex_node.parm("udim_enable") or tex_node.parm("udim")
                                if udim_parm:
                                    udim_parm.set(1)
                            # Try to connect to AO or multiply with base color
                            try:
                                multiply = mat_builder.createNode("Multiply", f"{safe_name}_ao_multiply")
                                if multiply:
                                    # Get base color connection
                                    base_color_input = surface.input(0) if surface.inputs() else None
                                    if base_color_input:
                                        multiply.setInput(0, base_color_input, 0)
                                    multiply.setInput(1, tex_node, 0)
                                    _connect_to_material_input(surface, "basecolor", multiply, 0)
                                else:
                                    _connect_to_material_input(surface, "ao", tex_node, 0)
                            except:
                                _connect_to_material_input(surface, "ao", tex_node, 0)
                        
                except Exception as tex_error:
                    print(f"Warning: Could not create texture node for {ttype}: {tex_error}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # Layout nodes
            mat_builder.layoutChildren()
            created_count += 1
            print(f"Created material: {mat_name}")
            
        except Exception as e:
            print(f"Error creating material {mat_name}: {e}")
    
    print(f"Successfully created {created_count} Karma materials!")
    return True

def ensure_udim_tag(path_str):
    """Convert UDIM numbers to <UDIM> tag format."""
    import re
    
    if "<UDIM>" in path_str:
        return path_str
    patterns = [
        (r"\.(\d{4})\.", ".<UDIM>."),
        (r"_(\d{4})\.", "_<UDIM>."),
        (r"\.(\d{4})_", ".<UDIM>_"),
        (r"_(\d{4})_", "_<UDIM>_"),
        (r"-(\d{4})\.", "-<UDIM>."),
        (r"-(\d{4})_", "-<UDIM>_"),
    ]
    for pat, rep in patterns:
        if re.search(pat, path_str):
            return re.sub(pat, rep, path_str)
    return path_str

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
    
    # Return format: (prefix, texture_type, ext, udim_token, variant)
    # This matches the format expected by the material creation functions
    # and is compatible with the fallback parser format: (prefix, ttype, ext, udim, variant)
    return prefix, texture_type, ext.lstrip(".") if ext else "", udim or "", raw_colorspace_name or ""
