"""
Material Loader Package
Material creation and loading tools for Houdini
"""

from .material_loader import show_material_loader
from .material_loader_menu_integration import setup_material_loader_tools

# Export backend functions for programmatic use
try:
    from .material_loader_redshift import create_usd_rs_materials_by_prefix
    from .material_loader_karma import create_karma_subnet_materials_by_prefix
    from .material_loader_helpers import (
        parse_texture_filename,
        fallback_parse_texture_filename,
        ensure_udim_tag,
        connect_to_material_input,
        get_texture_files,
        sanitize_material_name,
    )
    from .material_input_maps import (
        get_input_map,
        get_input_info,
        register_input_map,
        KARMA_INPUT_MAP,
        REDSHIFT_INPUT_MAP,
    )
    from .material_loader_registry import (
        register_engine,
        get_engine,
        get_available_engines,
        get_engine_display_names,
        is_engine_available,
    )
except ImportError:
    # Functions not available (e.g., outside Houdini)
    create_usd_rs_materials_by_prefix = None
    create_karma_subnet_materials_by_prefix = None
    parse_texture_filename = None
    fallback_parse_texture_filename = None
    ensure_udim_tag = None
    connect_to_material_input = None
    get_texture_files = None
    sanitize_material_name = None
    get_input_map = None
    get_input_info = None
    register_input_map = None
    KARMA_INPUT_MAP = None
    REDSHIFT_INPUT_MAP = None
    register_engine = None
    get_engine = None
    get_available_engines = None
    get_engine_display_names = None
    is_engine_available = None

__all__ = [
    'show_material_loader',
    'setup_material_loader_tools',
    # Backend functions
    'create_usd_rs_materials_by_prefix',
    'create_karma_subnet_materials_by_prefix',
    'parse_texture_filename',
    'fallback_parse_texture_filename',
    'ensure_udim_tag',
    'connect_to_material_input',
    'get_texture_files',
    'sanitize_material_name',
    # Input maps
    'get_input_map',
    'get_input_info',
    'register_input_map',
    'KARMA_INPUT_MAP',
    'REDSHIFT_INPUT_MAP',
    # Engine registry
    'register_engine',
    'get_engine',
    'get_available_engines',
    'get_engine_display_names',
    'is_engine_available',
]
