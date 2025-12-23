"""
Material Input Maps for different render engines
Maps texture types to material input names and indices for each engine.

This module uses a registry pattern to allow new engines to register their input maps.
"""

# MaterialX/Karma Standard Surface input map
KARMA_INPUT_MAP = {
    "basecolor": {"input_name": "base_color", "index": 0, "aliases": ["color", "albedo", "diffuse", "base_color"]},
    "roughness": {"input_name": "specular_roughness", "index": 1, "aliases": ["rough", "specular_roughness"]},
    "metallic": {"input_name": "metalness", "index": 2, "aliases": ["metalness", "metallicness"]},
    "normal": {"input_name": "normal", "index": 3, "aliases": ["normalmap"]},
    "displacement": {"input_name": "displacement", "index": 4, "aliases": ["height"]},
    "emission": {"input_name": "emission_color", "index": 5, "aliases": ["emissive", "emissioncolor"]},
    "opacity": {"input_name": "opacity", "index": 6, "aliases": ["alpha", "transparency"]},
    "ao": {"input_name": "ao", "index": 7, "aliases": ["occlusion", "ambient_occlusion"]},
    "translucent": {"input_name": "transmission", "index": 0, "aliases": ["translucent"]},
    "scatteringcolor": {"input_name": "subsurface_color", "index": 0, "aliases": ["scattering_color"]},
    "scattering": {"input_name": "subsurface", "index": 0, "aliases": ["scattering"]},
    "coatnormal": {"input_name": "coat_normal", "index": 0, "aliases": ["coat_normal"]},
    "coatopacity": {"input_name": "coat", "index": 0, "aliases": ["coat_opacity"]},
    "coatroughness": {"input_name": "coat_roughness", "index": 0, "aliases": ["coat_roughness"]},
}

# Redshift StandardMaterial input map
REDSHIFT_INPUT_MAP = {
    "basecolor": {"input_name": "base_color", "index": 0, "aliases": ["color", "albedo", "diffuse"]},
    "roughness": {"input_name": "refl_roughness", "index": 1, "aliases": ["rough", "refl_roughness"]},
    "metallic": {"input_name": "metalness", "index": 2, "aliases": ["metalness", "metallicness"]},
    "normal": {"input_name": "bump_input", "index": 3, "aliases": ["normalmap", "bump"]},
    "displacement": {"input_name": "displacement", "index": 4, "aliases": ["height"]},
    "emission": {"input_name": "emission_color", "index": 5, "aliases": ["emissive", "emissioncolor"]},
    "opacity": {"input_name": "opacity_color", "index": 6, "aliases": ["alpha", "transparency"]},
    "ao": {"input_name": "ao", "index": 7, "aliases": ["occlusion", "ambient_occlusion"]},
}

# Registry for input maps: maps engine name to input map dict
_INPUT_MAP_REGISTRY = {
    "karma": KARMA_INPUT_MAP,
    "redshift": REDSHIFT_INPUT_MAP,
}


def register_input_map(engine, input_map):
    """
    Register input map for an engine.
    
    Args:
        engine: Engine name (e.g., "arnold", "mantra")
        input_map: Dictionary mapping texture types to input info
    
    Example:
        from .material_input_maps import register_input_map
        ARNOLD_INPUT_MAP = {...}
        register_input_map("arnold", ARNOLD_INPUT_MAP)
    """
    _INPUT_MAP_REGISTRY[engine.lower()] = input_map


def get_input_map(engine="karma"):
    """
    Get input map for specified engine.
    
    Args:
        engine: Render engine name (e.g., "karma", "redshift", "arnold")
    
    Returns:
        dict: Input map for the engine, or KARMA_INPUT_MAP as fallback
    """
    engine_lower = engine.lower()
    return _INPUT_MAP_REGISTRY.get(engine_lower, KARMA_INPUT_MAP)


def get_input_info(texture_type, engine="karma"):
    """
    Get input information for a texture type.
    
    Args:
        texture_type: Texture type (e.g., "basecolor", "roughness")
        engine: Render engine ("karma" or "redshift")
    
    Returns:
        dict: Input info with "input_name" and "index", or None if not found
    """
    input_map = get_input_map(engine)
    texture_lower = texture_type.lower()
    
    # Direct match
    if texture_lower in input_map:
        return input_map[texture_lower]
    
    # Search in aliases
    for key, info in input_map.items():
        if texture_lower in info.get("aliases", []):
            return info
    
    return None


def get_available_inputs_for_engine(engine="karma"):
    """
    Get list of available input names for an engine.
    Used for unrecognized textures dialog.
    
    Args:
        engine: Render engine name (e.g., "karma", "redshift", "arnold")
    
    Returns:
        list: List of unique input names for the engine
    """
    input_map = get_input_map(engine)
    input_names = set()
    
    # Collect all input names from the map
    for texture_type, info in input_map.items():
        input_name = info.get("input_name")
        if input_name:
            input_names.add(input_name)
        # Also add aliases that might be input names
        for alias in info.get("aliases", []):
            if alias and not alias.startswith("_"):  # Skip internal aliases
                input_names.add(alias)
    
    # Return sorted list for consistent ordering
    return sorted(list(input_names))
