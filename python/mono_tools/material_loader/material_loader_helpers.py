"""
Helper functions for Material Loader
Shared utilities for texture parsing, UDIM handling, and material connections.
"""

import os
import re
from .material_input_maps import get_input_info, get_input_map, get_available_inputs_for_engine


DEBUG_CONNECTIONS = os.environ.get("MONO_MATERIAL_DEBUG_CONNECTIONS", "0") == "1"
DEBUG_LOG_PATH = os.environ.get("MONO_MATERIAL_DEBUG_FILE", "").strip()


def _debug_connection(message):
    if not DEBUG_CONNECTIONS:
        return
    formatted = f"[MaterialLoader][Connect] {message}"
    if DEBUG_LOG_PATH:
        try:
            with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as log_file:
                log_file.write(formatted + "\n")
        except Exception as log_error:
            # Fall back to console if writing to file fails
            print(f"[MaterialLoader][Connect][LogError] {log_error} -> {formatted}")
    else:
        print(formatted)


def parse_texture_filename(filename):
    """
    Parse texture filename to extract material name, type, UDIM, and colorspace info.
    
    Returns a 5-tuple: (prefix, texture_type, ext, udim_token, variant)
    - prefix: Material name prefix
    - texture_type: Type of texture (basecolor, roughness, etc.)
    - ext: File extension
    - udim_token: UDIM token if found (e.g., "1001" or "<UDIM>")
    - variant: Colorspace or other variant info
    
    Example:
        "my_mat_basecolor_1001.exr" -> ("my_mat", "basecolor", "exr", "1001", "")
    """
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
    return prefix, texture_type, ext.lstrip(".") if ext else "", udim or "", raw_colorspace_name or ""


def fallback_parse_texture_filename(filename: str):
    """
    Best-effort parser for common PBR texture naming.
    Used as fallback when main parser fails.
    
    Returns a 5-tuple: (prefix, ttype, ext, udim, variant)
    Example supported tokens: basecolor|albedo|diffuse, roughness, metallic|metalness,
    normal, height|displacement, specular, emissive, opacity|transparency, ao.
    Detects UDIM tokens: 1001-1999 or <UDIM> in name.
    """
    name = os.path.basename(filename)
    stem, ext = os.path.splitext(name)
    lower = stem.lower()

    # UDIM detection
    udim = None
    for token in ("<udim>", "{udim}"):
        if token in lower:
            udim = token
            break
    if udim is None:
        # 4-digit UDIM near the end
        for part in lower.replace(".", "_").split("_"):
            if part.isdigit() and len(part) == 4 and part.startswith("1"):
                udim = part
                break

    # Texture type mapping
    mapping = {
        "basecolor": "basecolor",
        "albedo": "basecolor",
        "diffuse": "basecolor",
        "color": "basecolor",
        "col": "basecolor",
        "base": "basecolor",
        "roughness": "roughness",
        "rough": "roughness",
        "metallic": "metallic",
        "metalness": "metallic",
        "metal": "metallic",
        "specular": "specular",
        "spec": "specular",
        "normal": "normal",
        "nrml": "normal",
        "nrm": "normal",
        "bump": "height",
        "height": "height",
        "displacement": "height",
        "disp": "height",
        "emissive": "emissive",
        "emit": "emissive",
        "emission": "emissive",
        "opacity": "opacity",
        "alpha": "opacity",
        "transparency": "opacity",
        "trans": "opacity",
        "ao": "occlusion",
        "occlusion": "occlusion",
    }

    detected = None
    token_hit = None
    parts = lower.replace("-", "_").split("_")
    for p in parts[::-1]:  # search from rightmost token
        if p in mapping:
            detected = mapping[p]
            token_hit = p
            break
    if detected is None:
        # Try suffix patterns like _bc, _r, _m, _n, _h, _d
        suffix_map = {
            "bc": "basecolor",
            "r": "roughness",
            "rough": "roughness",
            "m": "metallic",
            "metal": "metallic",
            "n": "normal",
            "norm": "normal",
            "h": "height",
            "d": "height",
            "s": "specular",
            "e": "emissive",
            "emit": "emissive",
            "a": "opacity",
        }
        last = parts[-1]
        if last in suffix_map:
            detected = suffix_map[last]

    prefix = stem
    variant = token_hit or ""
    if detected is None:
        return None
    return (prefix, detected, ext.lstrip("."), udim or "", variant)


def ensure_udim_tag(path_str):
    """Convert UDIM numbers to <UDIM> tag format."""
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


def connect_to_material_input(surface_node, input_name, source_node, output_index, engine="karma"):
    """
    Helper function to connect texture to material input by name or index.
    Uses engine-specific input maps based on user selection.
    
    Args:
        surface_node: The material/shader node to connect to
        input_name: Name of the input (e.g., "basecolor", "roughness", "metalness")
        source_node: The texture node to connect
        output_index: Output index of the source node (usually 0)
        engine: Render engine ("karma" or "redshift") - determines input map to use
    
    Returns:
        bool: True if connection succeeded, False otherwise
    """
    try:
        _debug_connection(f"Request connect input='{input_name}' engine='{engine}' "
                          f"source='{source_node.name() if source_node else 'None'}' "
                          f"surface='{surface_node.path() if surface_node else 'None'}'")
        # Get engine-specific input info
        input_info = get_input_info(input_name, engine)
        target_input_name = input_name  # Default to original name
        
        if input_info:
            # Use input name from map (e.g., "roughness" -> "specular_roughness" for Karma)
            target_input_name = input_info["input_name"]
            _debug_connection(f"Resolved input map: requested='{input_name}' -> target='{target_input_name}' "
                              f"index={input_info.get('index')}")
        
        # Try to find input by name (exact match first, then partial match)
        input_names = surface_node.inputNames()
        if input_names:
            # First try exact match with target input name (case-insensitive)
            for i, name in enumerate(input_names):
                if name and name.lower() == target_input_name.lower():
                    surface_node.setInput(i, source_node, output_index)
                    _debug_connection(f"Connected via exact target match '{name}' index={i}")
                    return True
            
            # Also try original input_name in case it matches directly
            for i, name in enumerate(input_names):
                if name and name.lower() == input_name.lower():
                    surface_node.setInput(i, source_node, output_index)
                    _debug_connection(f"Connected via exact original match '{name}' index={i}")
                    return True
            
            # Then try partial match (but avoid false matches like "coat_normal" for "normal")
            # For special types (coat, scattering, translucent), we need more precise matching
            special_types = ["coat", "scattering", "translucent", "transmission", "subsurface"]
            is_special_type = any(special in target_input_name.lower() or special in input_name.lower() 
                                 for special in special_types)
            
            for i, name in enumerate(input_names):
                if name:
                    name_lower = name.lower()
                    target_lower = target_input_name.lower()
                    input_lower = input_name.lower()
                    
                    # For special types, require more precise matching
                    if is_special_type:
                        # For special types, try exact word match or full substring match
                        # e.g., "coat_normal" should match "coat_normal" but not "normal"
                        if (target_lower == name_lower or 
                            (target_lower in name_lower and len(target_lower) > 5)):  # Require substantial match
                            surface_node.setInput(i, source_node, output_index)
                            _debug_connection(f"Connected special type '{input_name}' via match '{name}' index={i}")
                            return True
                        # Also try original input_name
                        if (input_lower == name_lower or 
                            (input_lower in name_lower and len(input_lower) > 5)):
                            surface_node.setInput(i, source_node, output_index)
                            _debug_connection(f"Connected special type '{input_name}' via original match '{name}' index={i}")
                            return True
                    else:
                        # For regular types, use existing partial match logic
                        # Try matching target_input_name first
                        if target_lower in name_lower:
                            # Avoid false matches: if input is "normal", don't match "coat_normal"
                            if target_lower == "normal" and "coat" in name_lower:
                                continue
                            # Avoid other false matches: if input is "roughness" or "specular_roughness", don't match "coat_roughness"
                            if (target_lower == "roughness" or target_lower == "specular_roughness" or 
                                target_lower == "refl_roughness") and "coat" in name_lower:
                                continue
                            surface_node.setInput(i, source_node, output_index)
                            _debug_connection(f"Connected via partial target match '{name}' index={i}")
                            return True
                        
                        # Fallback: try original input_name
                        if input_lower in name_lower:
                            if input_lower == "normal" and "coat" in name_lower:
                                continue
                            if (input_lower == "roughness" or input_lower == "specular_roughness" or 
                                input_lower == "refl_roughness") and "coat" in name_lower:
                                continue
                            surface_node.setInput(i, source_node, output_index)
                            _debug_connection(f"Connected via partial original match '{name}' index={i}")
                            return True
        
        # Fallback: use engine-specific input map by index
        # IMPORTANT: Don't use index=0 as fallback because multiple texture types share it
        # (coat, scattering, translucent all have index=0)
        # Only use index fallback for unique indices (1-7)
        if input_info:
            target_index = input_info["index"]
            # Only use index fallback if index is unique (not 0)
            # Index 0 is shared by multiple types, so name matching must succeed
            if target_index > 0 and target_index < len(surface_node.inputs() or []):
                surface_node.setInput(target_index, source_node, output_index)
                _debug_connection(f"Connected via index fallback {target_index}")
                return True
        
        # Last resort: try to set as parameter if available
        parm = surface_node.parm(target_input_name) or surface_node.parm(input_name) or \
              surface_node.parm(target_input_name.lower()) or surface_node.parm(input_name.lower())
        if parm:
            parm.set(source_node)
            _debug_connection(f"Connected via parameter '{parm.name()}'")
            return True
            
    except Exception as exc:
        _debug_connection(f"Connection failed with error: {exc}")
    return False
    return False


def get_texture_files(folder):
    """
    Get all texture files from a folder.
    
    Args:
        folder: Path to folder containing textures
    
    Returns:
        list: List of texture filenames
    """
    texture_files = []
    if not os.path.isdir(folder):
        return texture_files
    
    for f in os.listdir(folder):
        if f.lower().endswith(('.exr', '.jpg', '.jpeg', '.png', '.tif', '.tiff')):
            texture_files.append(f)
    
    return texture_files


def sanitize_material_name(mat_name):
    """
    Sanitize material name for Houdini node naming.
    
    Args:
        mat_name: Original material name
    
    Returns:
        str: Sanitized name safe for Houdini
    """
    import re
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', mat_name)
    safe_name = re.sub(r'_+', '_', safe_name).strip('_')
    if not safe_name or safe_name[0].isdigit():
        safe_name = 'mat_' + safe_name
    return safe_name
