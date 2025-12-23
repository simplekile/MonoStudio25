"""
Karma Material Creation for Mono Material Loader
Handles creation of Karma Material Builder materials from texture folders.
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


def create_karma_subnet_materials_by_prefix(folder, matlib_node, prefix_map, udim, position_offset=(0.0, 0.0)):
    """
    Create Karma materials from texture folder.
    
    Uses voptoolutils._setupMtlXBuilderSubnet() to create Material Builder nodes
    that are properly recognized by Solaris. This is the recommended method from
    SideFX forum: https://www.sidefx.com/forum/topic/95981/?page=1#post-422156
    
    The Material Builder will be configured with:
    - Material Flag set to True
    - MaterialX Builder parameters (tabmenumask, inherit_ctrl, shader_referencetype, shader_baseprimpath)
    - Proper tab menu mask for MaterialX/Karma nodes
    
    Falls back to basic MaterialBuilder or subnet creation if voptoolutils is unavailable.
    
    Args:
        folder: Path to folder containing textures
        matlib_node: Houdini node for material library (should be a Material Library in /stage)
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
    
    print(f"=== Creating Karma materials from {folder} ===")
    print(f"Material library: {matlib_node}")
    print(f"UDIM enabled: {udim}")
    print(f"DEBUG: Function create_karma_subnet_materials_by_prefix called")
    
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
            available_inputs = get_available_inputs_for_engine("karma")
            
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
            
            # Create Karma Material Builder using voptoolutils (recommended method from SideFX forum)
            # Reference: https://www.sidefx.com/forum/topic/95981/?page=1#post-422156
            # This ensures Solaris recognizes the Material Builder correctly
            mat_builder = None
            try:
                import voptoolutils
                
                # Create subnet first
                subnet_node = matlib_node.createNode("subnet", safe_name)
                
                # Setup Material Builder with proper configuration for Solaris
                mask = voptoolutils.KARMAMTLX_TAB_MASK
                print(f"DEBUG: Using KARMAMTLX_TAB_MASK: {mask}")
                print(f"DEBUG: render_context='kma'")
                mat_builder = voptoolutils._setupMtlXBuilderSubnet(
                    subnet_node=subnet_node,
                    destination_node=None,  # None because subnet already exists
                    name=safe_name,
                    mask=mask,
                    folder_label="Karma Material Builder",
                    render_context="kma"
                )
                print(f"DEBUG: Created mat_builder type: {mat_builder.type().name() if mat_builder else 'None'}")
                
                # If _setupMtlXBuilderSubnet returns None, use the subnet_node
                if mat_builder is None:
                    mat_builder = subnet_node
                
                # Verify it's not a Redshift material builder
                mat_builder_type = mat_builder.type().name().lower()
                if "redshift" in mat_builder_type or "rs_" in mat_builder_type:
                    print(f"⚠️  WARNING: voptoolutils created Redshift material builder instead of Karma!")
                    print(f"   Type: {mat_builder.type().name()}")
                    print(f"   This should not happen with render_context='kma'")
                    # Try to destroy and create manually
                    try:
                        mat_builder.destroy()
                        print(f"   Destroyed incorrect Redshift material builder")
                        # Create Karma Material Builder manually
                        mat_builder = matlib_node.createNode("subnet", safe_name)
                        # Set Material flag
                        mat_builder.setMaterialFlag(True)
                        # Create MaterialX Standard Surface inside
                        surface = mat_builder.createNode("mtlxstandard_surface", "mtlxstandard_surface")
                        print(f"   Created Karma Material Builder manually")
                    except Exception as e:
                        print(f"   Error creating manual Karma builder: {e}")
                        continue
                
                print(f"✓ Created Karma Material Builder using voptoolutils: {safe_name}")
                
            except ImportError:
                print(f"Warning: voptoolutils not available, falling back to basic subnet creation")
                try:
                    # Fallback: Try creating MaterialBuilder directly
                    mat_builder = matlib_node.createNode("MaterialBuilder", safe_name)
                    print(f"✓ Created MaterialBuilder node: {safe_name}")
                except Exception as e1:
                    try:
                        # Final fallback: Create basic subnet
                        mat_builder = matlib_node.createNode("subnet", safe_name)
                        print(f"⚠️  Created basic subnet (may not be recognized by Solaris): {safe_name}")
                    except Exception as e2:
                        print(f"Error: Could not create Material Builder for {safe_name}")
                        print(f"  voptoolutils error: {e1 if 'e1' in locals() else 'ImportError'}")
                        print(f"  Fallback error: {e2}")
                        continue
            
            if mat_builder is None:
                print(f"Error: Failed to create Material Builder for {safe_name}")
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
            
            # Find or create Material node inside the subnet
            surface = None
            
            if is_network and (node_type_name == "MaterialBuilder" or node_type_name == "subnet"):
                # Debug: List all existing children nodes
                existing_children = list(mat_builder.children())
                print(f"  Existing children nodes ({len(existing_children)}):")
                for child in existing_children:
                    print(f"    - {child.name()} ({child.type().name()})")
                
                # First, clean up any unwanted nodes (Redshift materials, etc.)
                children_to_remove = []
                for child in existing_children:
                    child_type = child.type().name().lower()
                    child_name_lower = child.name().lower()
                    # Remove Redshift-related nodes
                    if ("redshift" in child_type or "rs_" in child_type or 
                        "standardmaterial" in child_type or "redshift" in child_name_lower or
                        "rs_" in child_name_lower):
                        children_to_remove.append(child)
                        print(f"  Removing unwanted node: {child.name()} ({child.type().name()})")
                
                for child in children_to_remove:
                    child.destroy()
                
                # Find existing MaterialX Standard Surface node (created by voptoolutils)
                # voptoolutils creates mtlxstandard_surface node which is the main shader node
                remaining_children = list(mat_builder.children())
                for child in remaining_children:
                    child_type = child.type().name().lower()
                    child_name = child.name().lower()
                    
                    # Look for MaterialX Standard Surface (created by voptoolutils)
                    if "mtlxstandard_surface" in child_type or "mtlxstandard_surface" in child_name:
                        surface = child
                        print(f"  Found MaterialX Standard Surface: {surface.name()} ({surface.type().name()})")
                        break
                    # Also check for MaterialX Material nodes
                    elif "mtlx" in child_type and "material" in child_type:
                        if "redshift" not in child_type and "rs_" not in child_type:
                            surface = child
                            print(f"  Found MaterialX Material node: {surface.name()} ({surface.type().name()})")
                            break
                
                # If no MaterialX node found, try to find any Material node
                if surface is None:
                    for child in remaining_children:
                        child_type = child.type().name()
                        if any(mt in child_type for mt in ["Material", "MaterialX"]):
                            if ("redshift" not in child_type.lower() and "rs_" not in child_type.lower() and
                                "redshift" not in child.name().lower()):
                                surface = child
                                print(f"  Found Material node: {surface.name()} ({surface.type().name()})")
                                break
                
                # If still no node found, create one (shouldn't happen with voptoolutils)
                if surface is None:
                    try:
                        # Try MaterialX Standard Surface first
                        surface = mat_builder.createNode("mtlxstandard_surface", "mtlxstandard_surface1")
                        print(f"  Created MaterialX Standard Surface node")
                    except:
                        try:
                            # Fallback to MaterialX Material
                            surface = mat_builder.createNode("MaterialX", "material1")
                            print(f"  Created MaterialX node")
                        except:
                            try:
                            # Last fallback: Material::2.0
                                surface = mat_builder.createNode("Material::2.0", "material1")
                                print(f"  Created Material::2.0 node")
                            except Exception as e:
                                print(f"  Warning: Could not create Material node: {e}")
                                surface = mat_builder
            elif "Material" in node_type_name and not is_network:
                # For direct Material node (NOT a network), set texture paths directly to parameters
                surface = mat_builder
                print(f"Using Material node directly (parameter-based, not network)")
            else:
                # Fallback: try to find or create a material node
                surface = mat_builder
                print(f"Fallback: using {node_type_name} as surface")
            
            # Check if we're working with a network node (can create child nodes) or single node (parameters only)
            if is_network:
                # Create texture nodes for each type (network node approach)
                # Use MaterialX/Karma texture node types (preferred for Karma)
                # Use ONLY mtlximage to avoid Redshift nodes
                # NOTE: Do NOT use any fallback types as Houdini may create Redshift nodes
                texture_node_types = [
                    "mtlximage",          # MaterialX Image node (correct type)
                    # All fallbacks removed - may create Redshift nodes!
                ]
                
                def create_texture_node(name_suffix):
                    """Helper to create texture node with fallback types"""
                    print(f"    Attempting to create texture node '{name_suffix}'...")
                    for i, tex_type in enumerate(texture_node_types):
                        try:
                            print(f"      Trying {tex_type}...")
                            node = mat_builder.createNode(tex_type, f"{safe_name}_{name_suffix}")
                            print(f"    ✓ Created texture node: {node.name()} ({node.type().name()})")
                            return node
                        except Exception as e:
                            # Print error for debugging
                            print(f"      ✗ Failed to create {tex_type}: {str(e)[:100]}")
                            # Only continue if not last attempt
                            if i < len(texture_node_types) - 1:
                                continue
                    print(f"    ✗ Warning: Could not create texture node for {name_suffix} (tried all {len(texture_node_types)} types)")
                    return None
                
                SCALAR_INPUTS = {
                    "metalness",
                    "metallic",
                    "metallicness",
                    "specular_roughness",
                    "roughness",
                    "opacity",
                    "alpha",
                    "transparency",
                    "ao",
                    "ambient_occlusion",
                    "coat",
                    "coat_roughness",
                    "coatopacity",
                }

                def setup_and_connect_texture(tex_node, tex_path, input_name, input_index=0):
                    """Helper to set texture path, enable UDIM, and connect to material"""
                    if not tex_node:
                        return False
                    
                    # Set texture file path (if tex_path is provided)
                    if tex_path is not None:
                        file_set = False
                        for parm_name in ["filename", "file", "filepath"]:
                            parm = tex_node.parm(parm_name)
                            if parm:
                                parm.set(tex_path)
                                print(f"      Set {parm_name}: {tex_path}")
                                file_set = True
                                break
                        
                        if not file_set:
                            print(f"      ⚠️  Could not find file parameter")
                    
                    # Enable UDIM if needed
                    if udim:
                        udim_enabled = False
                        # Try various UDIM parameter names
                        for udim_parm_name in ["udim_enable", "udim", "enable_udim", "udim_enabled", "use_udim"]:
                            udim_parm = tex_node.parm(udim_parm_name)
                            if udim_parm:
                                udim_parm.set(1)
                                print(f"      Enabled UDIM (parameter: {udim_parm_name})")
                                udim_enabled = True
                                break
                        # Also try to set UDIM tag in filename if not already set
                        if not udim_enabled:
                            # Check if filename already has <UDIM> tag
                            file_parm = tex_node.parm("file") or tex_node.parm("filename") or tex_node.parm("filepath")
                            if file_parm:
                                current_path = file_parm.unexpandedString()
                                if "<UDIM>" not in current_path and "<udim>" not in current_path:
                                    # Path should already have <UDIM> from ensure_udim_tag, but check anyway
                                    pass

                    # Force scalar output for inputs that expect float
                    input_lower = input_name.lower()
                    if input_lower in SCALAR_INPUTS:
                        signature_parm = tex_node.parm("signature")
                        if signature_parm:
                            try:
                                signature_parm.set("float")
                                print(f"      Set signature=float for scalar input '{input_name}'")
                            except Exception as sig_error:
                                print(f"      ⚠️  Could not set signature to float: {sig_error}")
                    
                    # Try to connect to material input (use "karma" engine for MaterialX)
                    connected = connect_to_material_input(surface, input_name, tex_node, input_index, engine="karma")
                    if connected:
                        print(f"      ✓ Connected {input_name} texture to Material")
                        return True
                    else:
                        # Try direct connection by input index
                        try:
                            inputs = surface.inputs()
                            if inputs and input_index < len(inputs):
                                # Try to find input by name first
                                input_names = surface.inputNames()
                                if input_names and input_index < len(input_names):
                                    # Try connecting by name match
                                    for i, name in enumerate(input_names):
                                        if input_name.lower() in name.lower():
                                            surface.setInput(i, tex_node, 0)
                                            print(f"      ✓ Connected via input '{name}' (index {i})")
                                            return True
                                # Fallback: connect by index
                                surface.setInput(input_index, tex_node, 0)
                                print(f"      ✓ Connected via input index {input_index}")
                                return True
                        except Exception as e:
                            print(f"      ✗ Failed to connect {input_name} texture: {e}")
                    
                    return False
            else:
                # For single Material node, we'll set parameters directly
                def create_texture_node(name_suffix):
                    """Not needed for parameter-based approach"""
                    return None
            
            # Debug: Print texture information
            print(f"  Processing {len(textures)} texture types for {mat_name}:")
            for ttype, tex_path in textures.items():
                print(f"    - {ttype}: {tex_path}")
            
            for ttype, tex_path in textures.items():
                try:
                    print(f"  Creating texture node for {ttype}...")
                    # Normalize texture type to lowercase for matching
                    ttype_lower = ttype.lower()
                    
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
                    # Use lowercase comparison for case-insensitive matching
                    if ttype_lower in ["basecolor", "color", "albedo", "diffuse"]:
                        # Base Color - try different parameter names
                        tex_node = create_texture_node("basecolor")
                        if not tex_node:
                            print(f"      ✗ Failed to create texture node for {ttype}")
                            continue
                        if tex_node:
                            # Set texture file path
                            if tex_node.parm("filename"):
                                tex_node.parm("filename").set(tex_path)
                                print(f"      Set filename: {tex_path}")
                            elif tex_node.parm("file"):
                                tex_node.parm("file").set(tex_path)
                                print(f"      Set file: {tex_path}")
                            elif tex_node.parm("filepath"):
                                tex_node.parm("filepath").set(tex_path)
                                print(f"      Set filepath: {tex_path}")
                            
                            # Enable UDIM if needed
                            if udim:
                                udim_parm = tex_node.parm("udim_enable") or tex_node.parm("udim") or tex_node.parm("enable_udim")
                                if udim_parm:
                                    udim_parm.set(1)
                                    print(f"      Enabled UDIM")
                            
                            # Try to connect to basecolor input (use "karma" engine for MaterialX)
                            connected = connect_to_material_input(surface, "basecolor", tex_node, 0, engine="karma")
                            if connected:
                                print(f"      ✓ Connected {ttype} texture to Material")
                            else:
                                print(f"      ⚠️  Could not connect {ttype} texture (trying direct connection)")
                                # Try direct connection by index
                                try:
                                    if len(surface.inputs()) > 0:
                                        surface.setInput(0, tex_node, 0)
                                        print(f"      ✓ Connected via input index 0")
                                except:
                                    print(f"      ✗ Failed to connect {ttype} texture")
                        
                    elif ttype_lower in ["roughness", "rough"]:
                        # Roughness -> specular_roughness input
                        tex_node = create_texture_node("roughness")
                        if not tex_node:
                            print(f"      ✗ Failed to create texture node for {ttype}")
                            continue
                        setup_and_connect_texture(tex_node, tex_path, "specular_roughness", 1)
                        
                    elif ttype_lower in ["metallic", "metallicness", "metalness"]:
                        # Metallic -> metalness input
                        tex_node = create_texture_node("metallic")
                        if not tex_node:
                            print(f"      ✗ Failed to create texture node for {ttype}")
                            continue
                        setup_and_connect_texture(tex_node, tex_path, "metalness", 2)
                        
                    elif ttype_lower in ["normal", "normalmap"]:
                        # Normal - may need NormalMap node
                        tex_node = create_texture_node("normal")
                        if not tex_node:
                            print(f"      ✗ Failed to create texture node for {ttype}")
                            continue
                        if tex_node:
                            # Set texture file path and UDIM
                            file_set = False
                            for parm_name in ["filename", "file", "filepath"]:
                                parm = tex_node.parm(parm_name)
                                if parm:
                                    parm.set(tex_path)
                                    print(f"      Set {parm_name}: {tex_path}")
                                    file_set = True
                                    break
                            
                            if udim:
                                for udim_parm_name in ["udim_enable", "udim", "enable_udim"]:
                                    udim_parm = tex_node.parm(udim_parm_name)
                                    if udim_parm:
                                        udim_parm.set(1)
                                        print(f"      Enabled UDIM")
                                        break
                            
                            # Try to create MaterialX NormalMap node (avoid Redshift NormalMap)
                            try:
                                # Use ONLY mtlxnormalmap to avoid Redshift nodes
                                # NOTE: Do NOT use any fallback types as Houdini may create Redshift nodes
                                normal_map_types = [
                                    "mtlxnormalmap",          # MaterialX NormalMap (correct type)
                                    # All fallbacks removed - may create Redshift nodes!
                                ]
                                normal_map = None
                                for nm_type in normal_map_types:
                                    try:
                                        normal_map = mat_builder.createNode(nm_type, f"{safe_name}_normalmap")
                                        # Verify it's not a Redshift node
                                        node_type = normal_map.type().name().lower()
                                        if "redshift" in node_type or "rs_" in node_type:
                                            print(f"      ⚠️  Created Redshift NormalMap instead of MaterialX, destroying...")
                                            normal_map.destroy()
                                            normal_map = None
                                            continue
                                        print(f"      Created NormalMap node: {normal_map.name()} ({normal_map.type().name()})")
                                        break
                                    except Exception as e:
                                        # Only print error for last attempt
                                        if nm_type == normal_map_types[-1]:
                                            print(f"      ✗ Failed to create NormalMap: {e}")
                                        continue
                                
                                if normal_map:
                                    normal_map.setInput(0, tex_node, 0)
                                    # Connect to normal input (not coat_normal) - use "karma" engine
                                    connected = connect_to_material_input(surface, "normal", normal_map, 0, engine="karma")
                                    if connected:
                                        print(f"      ✓ Connected NormalMap to normal input")
                                    if not connected:
                                        # Try to find normal input by name (avoid coat_normal)
                                        try:
                                            input_names = surface.inputNames()
                                            if input_names:
                                                for i, name in enumerate(input_names):
                                                    # Match "normal" but not "coat_normal"
                                                    if name and name.lower() == "normal" and "coat" not in name.lower():
                                                        surface.setInput(i, normal_map, 0)
                                                        print(f"      ✓ Connected NormalMap via input '{name}' (index {i})")
                                                        connected = True
                                                        break
                                        except:
                                            pass
                                    if not connected:
                                        # Fallback: try input index 3
                                        try:
                                            if len(surface.inputs()) > 3:
                                                surface.setInput(3, normal_map, 0)
                                                print(f"      ✓ Connected NormalMap via input index 3")
                                        except:
                                            print(f"      ✗ Failed to connect NormalMap")
                                else:
                                    # Connect texture directly to normal input - use "karma" engine
                                    connected = connect_to_material_input(surface, "normal", tex_node, 0, engine="karma")
                                    if not connected:
                                        # Try to find normal input by name (avoid coat_normal)
                                        try:
                                            input_names = surface.inputNames()
                                            if input_names:
                                                for i, name in enumerate(input_names):
                                                    if name and name.lower() == "normal" and "coat" not in name.lower():
                                                        surface.setInput(i, tex_node, 0)
                                                        print(f"      ✓ Connected normal texture via input '{name}' (index {i})")
                                                        connected = True
                                                        break
                                        except:
                                            pass
                                    if not connected:
                                        # Fallback: try input index 3
                                        try:
                                            if len(surface.inputs()) > 3:
                                                surface.setInput(3, tex_node, 0)
                                                print(f"      ✓ Connected normal texture via input index 3")
                                        except:
                                            print(f"      ✗ Failed to connect normal texture")
                            except Exception as e:
                                print(f"      Warning: Could not create NormalMap, connecting texture directly: {e}")
                                # Connect texture directly - use "karma" engine
                                connected = connect_to_material_input(surface, "normal", tex_node, 0, engine="karma")
                                if not connected:
                                    try:
                                        input_names = surface.inputNames()
                                        if input_names:
                                            for i, name in enumerate(input_names):
                                                if name and name.lower() == "normal" and "coat" not in name.lower():
                                                    surface.setInput(i, tex_node, 0)
                                                    print(f"      ✓ Connected normal texture via input '{name}' (index {i})")
                                                    break
                                    except:
                                        pass
                        
                    elif ttype_lower in ["height", "displacement"]:
                        # Displacement/Height - connect to mtlxdisplacement node if available
                        # First check if mtlxdisplacement node exists
                        displacement_node = None
                        for child in mat_builder.children():
                            if "displacement" in child.type().name().lower():
                                displacement_node = child
                                print(f"      Found displacement node: {displacement_node.name()}")
                                break
                        
                        tex_node = create_texture_node("height")
                        if not tex_node:
                            print(f"      ✗ Failed to create texture node for {ttype}")
                            continue
                        
                        # If displacement node exists, connect to it; otherwise connect to surface
                        if displacement_node:
                            setup_and_connect_texture(tex_node, tex_path, "displacement", 0)
                        else:
                            setup_and_connect_texture(tex_node, tex_path, "displacement", 4)
                        
                    elif ttype_lower in ["emissive", "emission", "emissioncolor"]:
                        # Emissive/Emission Color
                        tex_node = create_texture_node("emissive")
                        if tex_node:
                            # Try emission_color first (MaterialX naming)
                            connected = setup_and_connect_texture(tex_node, tex_path, "emission_color", 5)
                            if not connected:
                                setup_and_connect_texture(tex_node, tex_path, "emission", 5)
                        else:
                            print(f"      ✗ Failed to create texture node for {ttype}")
                        
                    elif ttype_lower in ["opacity", "alpha", "transparency"]:
                        # Opacity
                        tex_node = create_texture_node("opacity")
                        if not tex_node:
                            print(f"      ✗ Failed to create texture node for {ttype}")
                            continue
                        setup_and_connect_texture(tex_node, tex_path, "opacity", 6)
                    
                    elif ttype_lower == "translucent":
                        # Translucent/Transmission
                        tex_node = create_texture_node("translucent")
                        if tex_node:
                            # MaterialX uses transmission_color for translucent
                            connected = setup_and_connect_texture(tex_node, tex_path, "transmission_color", 0)
                            if not connected:
                                setup_and_connect_texture(tex_node, tex_path, "translucent", 0)
                        else:
                            print(f"      ✗ Failed to create texture node for {ttype}")
                    
                    elif ttype_lower in ["scatteringcolor", "scattering_color"]:
                        # Subsurface Scattering Color
                        tex_node = create_texture_node("scatteringcolor")
                        if tex_node:
                            # MaterialX uses subsurface_color
                            connected = setup_and_connect_texture(tex_node, tex_path, "subsurface_color", 0)
                            if not connected:
                                setup_and_connect_texture(tex_node, tex_path, "scattering_color", 0)
                        else:
                            print(f"      ✗ Failed to create texture node for {ttype}")
                    
                    elif ttype_lower == "scattering":
                        # Subsurface Scattering Amount
                        tex_node = create_texture_node("scattering")
                        if tex_node:
                            # MaterialX uses subsurface parameter
                            connected = setup_and_connect_texture(tex_node, tex_path, "subsurface", 0)
                            if not connected:
                                setup_and_connect_texture(tex_node, tex_path, "scattering", 0)
                        else:
                            print(f"      ✗ Failed to create texture node for {ttype}")
                    
                    elif ttype_lower in ["coatnormal", "coat_normal"]:
                        # Coat Normal
                        tex_node = create_texture_node("coatnormal")
                        if tex_node:
                            connected = setup_and_connect_texture(tex_node, tex_path, "coat_normal", 0)
                            if not connected:
                                # Try creating MaterialX normal map for coat (avoid Redshift)
                                try:
                                    # Use ONLY mtlxnormalmap to avoid Redshift nodes
                                    normal_map = None
                                    try:
                                        normal_map = mat_builder.createNode("mtlxnormalmap", f"{safe_name}_coatnormalmap")
                                        # Verify it's not a Redshift node
                                        node_type = normal_map.type().name().lower()
                                        if "redshift" in node_type or "rs_" in node_type:
                                            print(f"      ⚠️  Created Redshift NormalMap instead of MaterialX, destroying...")
                                            normal_map.destroy()
                                            normal_map = None
                                    except Exception as e:
                                        print(f"      ✗ Failed to create mtlxnormalmap for coat: {e}")
                                    if normal_map:
                                        normal_map.setInput(0, tex_node, 0)
                                        setup_and_connect_texture(normal_map, None, "coat_normal", 0)
                                except:
                                    pass
                        else:
                            print(f"      ✗ Failed to create texture node for {ttype}")
                    
                    elif ttype_lower in ["coatopacity", "coat_opacity"]:
                        # Coat Opacity
                        tex_node = create_texture_node("coatopacity")
                        if tex_node:
                            setup_and_connect_texture(tex_node, tex_path, "coat", 0)
                        else:
                            print(f"      ✗ Failed to create texture node for {ttype}")
                    
                    elif ttype_lower in ["coatroughness", "coat_roughness"]:
                        # Coat Roughness
                        tex_node = create_texture_node("coatroughness")
                        if tex_node:
                            setup_and_connect_texture(tex_node, tex_path, "coat_roughness", 0)
                        else:
                            print(f"      ✗ Failed to create texture node for {ttype}")
                    
                    elif ttype_lower in ["id", "makeup"]:
                        # ID and Makeup textures - typically not connected to material, just stored
                        tex_node = create_texture_node(ttype.lower())
                        if tex_node:
                            # Set texture path but don't connect (these are utility textures)
                            for parm_name in ["filename", "file", "filepath"]:
                                parm = tex_node.parm(parm_name)
                                if parm:
                                    parm.set(tex_path)
                                    print(f"      Set {parm_name} for utility texture {ttype}: {tex_path}")
                                    break
                            if udim:
                                for udim_parm_name in ["udim_enable", "udim", "enable_udim"]:
                                    udim_parm = tex_node.parm(udim_parm_name)
                                    if udim_parm:
                                        udim_parm.set(1)
                                        print(f"      Enabled UDIM for {ttype}")
                                        break
                            print(f"      ℹ️  {ttype} texture created (utility texture, not connected to material)")
                        else:
                            print(f"      ✗ Failed to create texture node for {ttype}")
                        
                    elif ttype_lower in ["occlusion", "ao"]:
                        # AO - typically multiply with base color or connect directly
                        tex_node = create_texture_node("ao")
                        if tex_node:
                            # Set texture file path and UDIM
                            file_set = False
                            for parm_name in ["filename", "file", "filepath"]:
                                parm = tex_node.parm(parm_name)
                                if parm:
                                    parm.set(tex_path)
                                    print(f"      Set {parm_name}: {tex_path}")
                                    file_set = True
                                    break
                            
                            if udim:
                                for udim_parm_name in ["udim_enable", "udim", "enable_udim"]:
                                    udim_parm = tex_node.parm(udim_parm_name)
                                    if udim_parm:
                                        udim_parm.set(1)
                                        print(f"      Enabled UDIM")
                                        break
                            
                            # Try to connect to AO input first
                            connected = setup_and_connect_texture(tex_node, None, "ao", 7)
                            
                            # If no AO input, try multiplying with base color
                            if not connected:
                                try:
                                    # Use ONLY mtlxmultiply to avoid Redshift nodes
                                    # NOTE: Do NOT use any fallback types as Houdini may create Redshift nodes
                                    multiply_types = ["mtlxmultiply"]
                                    multiply = None
                                    for mult_type in multiply_types:
                                        try:
                                            multiply = mat_builder.createNode(mult_type, f"{safe_name}_ao_multiply")
                                            # Verify it's not a Redshift node
                                            node_type = multiply.type().name().lower()
                                            if "redshift" in node_type or "rs_" in node_type:
                                                print(f"      ⚠️  Created Redshift Multiply instead of MaterialX, destroying...")
                                                multiply.destroy()
                                                multiply = None
                                                continue
                                            print(f"      Created Multiply node for AO: {multiply.name()} ({multiply.type().name()})")
                                            break
                                        except Exception as e:
                                            # Only print error for last attempt
                                            if mult_type == multiply_types[-1]:
                                                print(f"      ✗ Failed to create MaterialX Multiply: {e}")
                                            continue
                                    
                                    if multiply:
                                        # Get base color connection
                                        base_color_input = surface.input(0) if surface.inputs() else None
                                        if base_color_input:
                                            multiply.setInput(0, base_color_input, 0)
                                        multiply.setInput(1, tex_node, 0)
                                        # Connect multiply result to basecolor
                                        connected = setup_and_connect_texture(multiply, None, "basecolor", 0)
                                        if connected:
                                            print(f"      ✓ Connected AO via Multiply to basecolor")
                                except Exception as e:
                                    print(f"      ⚠️  Could not create Multiply for AO: {e}")
                    else:
                        # Texture type not handled - check if user configured it
                        texture_key = f"{mat_name}::{ttype}"
                        choice = texture_choices.get(texture_key)
                        
                        if choice and choice["action"] == "skip":
                            print(f"      ⚠️  Texture type '{ttype}' skipped (user choice)")
                            continue
                        elif choice and choice["action"] == "connect":
                            # Create and connect to user-selected input
                            input_name = choice.get("input")
                            if input_name:
                                tex_node = create_texture_node(ttype.lower())
                                if tex_node:
                                    setup_and_connect_texture(tex_node, tex_path, input_name, 0)
                                    print(f"      ✓ Connected '{ttype}' to '{input_name}' (user choice)")
                                else:
                                    print(f"      ✗ Failed to create texture node for '{ttype}'")
                            else:
                                print(f"      ⚠️  No input selected for '{ttype}' - creating unconnected")
                                # Fall through to unconnected
                                choice = {"action": "unconnected"}
                        
                        # Default or unconnected: create node but don't connect
                        if not choice or choice["action"] == "unconnected":
                            print(f"      ⚠️  Texture type '{ttype}' not recognized - creating as unconnected utility texture")
                            tex_node = create_texture_node(ttype.lower())
                            if tex_node:
                                # Set texture path but don't connect (user can connect manually)
                                for parm_name in ["filename", "file", "filepath"]:
                                    parm = tex_node.parm(parm_name)
                                    if parm:
                                        parm.set(tex_path)
                                        print(f"      Set {parm_name} for unrecognized texture '{ttype}': {tex_path}")
                                        break
                                if udim:
                                    for udim_parm_name in ["udim_enable", "udim", "enable_udim"]:
                                        udim_parm = tex_node.parm(udim_parm_name)
                                        if udim_parm:
                                            udim_parm.set(1)
                                            print(f"      Enabled UDIM for {ttype}")
                                            break
                                print(f"      ℹ️  '{ttype}' texture created but not connected (manual connection required)")
                            else:
                                print(f"      ✗ Failed to create texture node for unrecognized type: {ttype}")
                        
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
                if prefix in materials:
                    # Material exists, find it and add textures
                    safe_name = sanitize_material_name(prefix)
                    # Find existing material builder
                    existing_builder = None
                    for child in matlib_node.children():
                        if child.name() == safe_name:
                            existing_builder = child
                            break
                    
                    if existing_builder:
                        mat_builder = existing_builder
                        # Find surface node
                        surface = None
                        for child in mat_builder.children():
                            child_type = child.type().name().lower()
                            if "mtlxstandard_surface" in child_type:
                                surface = child
                                break
                        if not surface:
                            surface = mat_builder
                    else:
                        print(f"  ⚠️  Material '{prefix}' not found, skipping unrecognized textures")
                        continue
                else:
                    # Create new material for unrecognized textures
                    safe_name = sanitize_material_name(prefix)
                    print(f"  Creating material for unrecognized textures: {safe_name}")
                    
                    # Create material builder (simplified - reuse existing logic)
                    try:
                        import voptoolutils
                        subnet_node = matlib_node.createNode("subnet", safe_name)
                        mask = voptoolutils.KARMAMTLX_TAB_MASK
                        mat_builder = voptoolutils._setupMtlXBuilderSubnet(
                            subnet_node=subnet_node,
                            destination_node=None,
                            name=safe_name,
                            mask=mask,
                            folder_label="Karma Material Builder",
                            render_context="kma"
                        )
                        if mat_builder is None:
                            mat_builder = subnet_node
                    except:
                        mat_builder = matlib_node.createNode("subnet", safe_name)
                    
                    # Find or create surface
                    surface = None
                    for child in mat_builder.children():
                        if "mtlxstandard_surface" in child.type().name().lower():
                            surface = child
                            break
                    if not surface:
                        try:
                            surface = mat_builder.createNode("mtlxstandard_surface", "mtlxstandard_surface")
                        except:
                            surface = mat_builder
                
                # Process each unrecognized texture
                is_network = mat_builder.isNetwork()
                
                def create_texture_node(name_suffix):
                    if not is_network:
                        return None
                    try:
                        return mat_builder.createNode("mtlximage", f"{safe_name}_{name_suffix}")
                    except:
                        return None
                
                for ttype, tex_path, filename, choice in texture_list:
                    print(f"  Processing unrecognized texture: {filename} (type: {ttype})")
                    
                    if choice["action"] == "connect":
                        input_name = choice.get("input")
                        if input_name:
                            tex_node = create_texture_node(ttype.lower())
                            if tex_node:
                                # Set texture path
                                for parm_name in ["filename", "file", "filepath"]:
                                    parm = tex_node.parm(parm_name)
                                    if parm:
                                        parm.set(tex_path)
                                        break
                                if udim:
                                    for udim_parm_name in ["udim_enable", "udim", "enable_udim"]:
                                        udim_parm = tex_node.parm(udim_parm_name)
                                        if udim_parm:
                                            udim_parm.set(1)
                                            break
                                # Connect to input
                                setup_and_connect_texture(tex_node, None, input_name, 0)
                                print(f"    ✓ Connected '{ttype}' to '{input_name}'")
                            else:
                                print(f"    ✗ Failed to create texture node for '{ttype}'")
                    
                    elif choice["action"] == "unconnected":
                        tex_node = create_texture_node(ttype.lower())
                        if tex_node:
                            # Set texture path but don't connect
                            for parm_name in ["filename", "file", "filepath"]:
                                parm = tex_node.parm(parm_name)
                                if parm:
                                    parm.set(tex_path)
                                    break
                            if udim:
                                for udim_parm_name in ["udim_enable", "udim", "enable_udim"]:
                                    udim_parm = tex_node.parm(udim_parm_name)
                                    if udim_parm:
                                        udim_parm.set(1)
                                        break
                            print(f"    ℹ️  Created unconnected texture node for '{ttype}'")
                
                # Layout nodes
                if is_network:
                    mat_builder.layoutChildren()
                
            except Exception as e:
                print(f"  Error processing unrecognized textures for '{prefix}': {e}")
    
    print(f"Successfully created {created_count} Karma materials!")
    return True
