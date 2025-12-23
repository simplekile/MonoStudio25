"""
Redshift Material Creation for Mono Material Loader
Handles creation of Redshift USD materials from texture folders.
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

# Import Qt for dialog (optional - only if available)
try:
    from .qt import QtWidgets
except:
    try:
        from mono_tools.qt import QtWidgets
    except:
        QtWidgets = None

# Import dialog for unrecognized textures
try:
    from .unrecognized_textures_dialog import UnrecognizedTexturesDialog
except ImportError:
    try:
        from mono_tools.material_loader.unrecognized_textures_dialog import UnrecognizedTexturesDialog
    except ImportError:
        UnrecognizedTexturesDialog = None


def create_usd_rs_materials_by_prefix(folder, matlib_node, prefix_map, udim, position_offset=(0.0, 0.0)):
    """
    Create Redshift materials from texture folder.
    
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
    
    print(f"Creating Redshift materials from {folder}")
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
    
    # Group textures by material name (prefix)
    materials = {}
    unrecognized_textures = []  # Track unrecognized textures: (mat_name, ttype, tex_path, filename)
    
    for filename in texture_files:
        parsed = parser(filename)
        if parsed:
            # parse_texture_filename returns: (prefix, texture_type, ext, udim_token, variant)
            prefix, ttype, ext, udim_token, variant = parsed
            if prefix not in materials:
                materials[prefix] = {}
            # Convert UDIM numbers to <UDIM> tag if UDIM is enabled
            tex_path = os.path.join(folder, filename)
            if udim and udim_token:
                tex_path = ensure_udim_tag(tex_path)
            
            materials[prefix][ttype] = tex_path
        else:
            # Texture couldn't be parsed - will be handled separately
            # Try to extract prefix from filename for grouping
            name_without_ext = os.path.splitext(filename)[0]
            parts = name_without_ext.replace("-", "_").split("_")
            if len(parts) > 1:
                prefix = "_".join(parts[:-1])
                ttype = parts[-1]
            else:
                prefix = "unrecognized"
                ttype = name_without_ext
            
            tex_path = os.path.join(folder, filename)
            if udim:
                # Check if filename has UDIM pattern
                tex_path = ensure_udim_tag(tex_path)
            
            unrecognized_textures.append((prefix, ttype, tex_path, filename))
            print(f"  ⚠️  Unrecognized texture: {filename} -> prefix: '{prefix}', type: '{ttype}'")
    
    # Show dialog for unrecognized textures if any
    texture_choices = {}
    if unrecognized_textures:
        try:
            import hou
            # Get available inputs from material input map for current engine
            from .material_input_maps import get_available_inputs_for_engine
            available_inputs = get_available_inputs_for_engine("redshift")
            
            # Show dialog if QtWidgets and dialog are available
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
                    print("⚠️  User cancelled unrecognized textures dialog - skipping unrecognized textures")
            else:
                print("⚠️  Dialog not available - skipping unrecognized textures")
        except Exception as e:
            print(f"⚠️  Could not show unrecognized textures dialog: {e}")
            print("  Skipping unrecognized textures")
    
    print(f"Found {len(materials)} materials: {list(materials.keys())}")
    
    # Create materials
    created_count = 0
    for mat_name, textures in materials.items():
        try:
            safe_name = sanitize_material_name(mat_name)
            
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
            
            # Create texture nodes for each type
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
                        # Texture type not handled - check if user configured it
                        texture_key = f"{mat_name}::{ttype}"
                        choice = texture_choices.get(texture_key)
                        
                        if choice and choice["action"] == "skip":
                            print(f"      ⚠️  Texture type '{ttype}' skipped (user choice)")
                            continue
                        elif choice and choice["action"] == "connect":
                            # Use user-selected input
                            input_name = choice.get("input")
                            if input_name:
                                # Find matching port
                                port_name = None
                                for i, nm in enumerate(rs_mat.inputNames() or []):
                                    if nm and input_name.lower() in nm.lower():
                                        port_name = nm
                                        break
                                if port_name:
                                    print(f"      ✓ Using user-selected input '{input_name}' for '{ttype}'")
                                else:
                                    print(f"      ⚠️  Input '{input_name}' not found, using fallback")
                                    port_name = "base_color"
                            else:
                                port_name = "base_color"
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
    
    # Process unrecognized textures that were configured by user
    if unrecognized_textures and texture_choices:
        print(f"\n=== Processing {len(unrecognized_textures)} unrecognized texture(s) ===")
        
        # Group unrecognized textures by material prefix
        unrecognized_by_material = {}
        for prefix, ttype, tex_path, filename in unrecognized_textures:
            texture_key = f"{prefix}::{ttype}"
            choice = texture_choices.get(texture_key)
            
            if not choice or choice["action"] == "skip":
                continue  # Skip this texture
            
            if prefix not in unrecognized_by_material:
                unrecognized_by_material[prefix] = []
            unrecognized_by_material[prefix].append((ttype, tex_path, filename, choice))
        
        # Process each material's unrecognized textures
        for prefix, texture_list in unrecognized_by_material.items():
            try:
                # Check if material already exists
                safe_name = sanitize_material_name(prefix)
                existing_builder = None
                for child in matlib_node.children():
                    if child.name() == safe_name:
                        existing_builder = child
                        break
                
                if not existing_builder:
                    print(f"  ⚠️  Material '{prefix}' not found, skipping unrecognized textures")
                    continue
                
                mat_builder = existing_builder
                rs_mat = None
                for child in mat_builder.children():
                    if "standardmaterial" in child.name().lower():
                        rs_mat = child
                        break
                
                if not rs_mat:
                    print(f"  ⚠️  StandardMaterial not found in '{prefix}', skipping unrecognized textures")
                    continue
                
                # Process each unrecognized texture
                for ttype, tex_path, filename, choice in texture_list:
                    print(f"  Processing unrecognized texture: {filename} (type: {ttype})")
                    
                    if choice["action"] == "connect":
                        input_name = choice.get("input")
                        if input_name:
                            # Create texture sampler
                            ts = mat_builder.createNode("redshift::TextureSampler", f"TS_{ttype}")
                            tex_parm = ts.parm("tex0")
                            if tex_parm:
                                tex_parm.set(tex_path)
                            
                            if udim:
                                udim_parm = ts.parm("udim_enable")
                                if udim_parm:
                                    udim_parm.set(1)
                            
                            # Find and connect to input
                            port_idx = None
                            for i, nm in enumerate(rs_mat.inputNames() or []):
                                if nm and input_name.lower() in nm.lower():
                                    port_idx = i
                                    break
                            
                            if port_idx is not None:
                                rs_mat.setInput(port_idx, ts, 0)
                                print(f"    ✓ Connected '{ttype}' to '{input_name}'")
                            else:
                                print(f"    ⚠️  Input '{input_name}' not found for '{ttype}'")
                    
                    elif choice["action"] == "unconnected":
                        # Create texture sampler but don't connect
                        ts = mat_builder.createNode("redshift::TextureSampler", f"TS_{ttype}")
                        tex_parm = ts.parm("tex0")
                        if tex_parm:
                            tex_parm.set(tex_path)
                        
                        if udim:
                            udim_parm = ts.parm("udim_enable")
                            if udim_parm:
                                udim_parm.set(1)
                        
                        print(f"    ℹ️  Created unconnected texture node for '{ttype}'")
                
                # Layout nodes
                mat_builder.layoutChildren()
                
            except Exception as e:
                print(f"  Error processing unrecognized textures for '{prefix}': {e}")
    
    print(f"Successfully created {created_count} Redshift materials!")
    return True
