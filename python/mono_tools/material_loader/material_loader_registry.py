"""
Material Loader Engine Registry
Dynamic engine registration and discovery system for material creation engines.

This module provides a registry pattern that allows new render engines to be
added without modifying the main UI or core logic.
"""

# Engine registry: maps engine name to engine info
_ENGINE_REGISTRY = {}


def register_engine(engine_name, create_function, display_name=None):
    """
    Register a new material creation engine.
    
    Args:
        engine_name: Internal engine name (e.g., "karma", "redshift", "arnold")
        create_function: Function to create materials with signature:
            create_function(folder, matlib_node, prefix_map, udim, position_offset)
        display_name: Human-readable name (defaults to engine_name.title())
    
    Example:
        from .material_loader_registry import register_engine
        register_engine("arnold", create_arnold_materials_by_prefix, "Arnold")
    """
    if not create_function:
        raise ValueError(f"create_function cannot be None for engine '{engine_name}'")
    
    _ENGINE_REGISTRY[engine_name.lower()] = {
        "name": engine_name.lower(),
        "display_name": display_name or engine_name.title(),
        "create_function": create_function,
    }


def get_engine(engine_name):
    """
    Get engine info by name.
    
    Args:
        engine_name: Engine name (case-insensitive)
    
    Returns:
        dict: Engine info with keys: "name", "display_name", "create_function"
        None: If engine not found
    """
    return _ENGINE_REGISTRY.get(engine_name.lower())


def get_available_engines():
    """
    Get list of all registered engine names.
    
    Returns:
        list: Sorted list of engine names (e.g., ["karma", "redshift"])
    """
    return sorted(_ENGINE_REGISTRY.keys())


def get_engine_display_names():
    """
    Get dict mapping engine names to display names.
    
    Returns:
        dict: {engine_name: display_name, ...}
    """
    return {k: v["display_name"] for k, v in _ENGINE_REGISTRY.items()}


def is_engine_available(engine_name):
    """
    Check if an engine is registered and available.
    
    Args:
        engine_name: Engine name (case-insensitive)
    
    Returns:
        bool: True if engine is registered
    """
    return engine_name.lower() in _ENGINE_REGISTRY


# Auto-register existing engines on import
def _auto_register_engines():
    """Automatically register engines that are available."""
    # Register Karma
    try:
        from .material_loader_karma import create_karma_subnet_materials_by_prefix
        register_engine("karma", create_karma_subnet_materials_by_prefix, "Karma")
    except ImportError:
        pass
    
    # Register Redshift
    try:
        from .material_loader_redshift import create_usd_rs_materials_by_prefix
        register_engine("redshift", create_usd_rs_materials_by_prefix, "Redshift")
    except ImportError:
        pass


# Auto-register on module import
_auto_register_engines()

