import os, re, platform, subprocess, shutil, json
from datetime import datetime
from mono_tools.qt import QtCore, QtGui, QtWidgets
import hou

# Debug flag - set to True to enable verbose file scanning logs
# Set MONO_DEBUG=1 environment variable to enable debug output
DEBUG = os.environ.get('MONO_DEBUG', '0').lower() in ('1', 'true', 'yes')

# Debug print helper - only prints if DEBUG is enabled
def debug_print(*args, **kwargs):
    """Print only if DEBUG mode is enabled"""
    if DEBUG:
        print(*args, **kwargs)

ORG="Mono"; APP="FileManager"
SUBPATH=os.path.join("02_shots","03_lighting")
HOUDINI_EXTS={".hip",".hiplc",".hipnc"}
VER_RX=re.compile(r"(?:^|[_\.])v(\d{1,4})(?:[_\.]|$)", re.IGNORECASE)
SHOT_RX=re.compile(r'^(Sh\d+|SH\d+)', re.IGNORECASE)

def human_size(b):
    try: b=float(b)
    except: return "-"
    for u in ["B","KB","MB","GB","TB"]:
        if b<1024: return f"{b:3.1f} {u}"
        b/=1024
    return f"{b:.1f} PB"

def open_in_explorer(path):
    if not path or not os.path.exists(path):
        hou.ui.displayMessage(f"Đường dẫn không tồn tại:\n{path or '<empty>'}", severity=hou.severityType.Warning); return
    target_path = path if os.path.isdir(path) else os.path.dirname(path)
    if not os.path.isdir(target_path):
        hou.ui.displayMessage(f"Thư mục không tồn tại:\n{target_path}", severity=hou.severityType.Warning); return
    sys_name = platform.system()
    try:
        if sys_name == "Windows":
            if os.path.isfile(path): subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
            else: subprocess.Popen(["explorer", os.path.normpath(target_path)])
        elif sys_name == "Darwin": subprocess.Popen(["open", target_path])
        else: subprocess.Popen(["xdg-open", target_path])
    except Exception as e:
        hou.ui.displayMessage(f"Lỗi khi mở explorer:\n{str(e)}", severity=hou.severityType.Error)

def get_render_folder_path(hip_file_path):
    if not hip_file_path or hip_file_path == "untitled.hip": return None
    try:
        hip_dir = os.path.dirname(hip_file_path)
        filename = os.path.basename(hip_file_path)
        filename_no_ext = os.path.splitext(filename)[0]
        current_dir = hip_dir
        project_root = None
        for _ in range(5):
            if os.path.exists(os.path.join(current_dir, "render")):
                project_root = current_dir; break
            parent = os.path.dirname(current_dir)
            if parent == current_dir: break
            current_dir = parent
        if not project_root:
            project_root = os.path.dirname(hip_dir)
        return os.path.join(project_root, "render", "Final", filename_no_ext)
    except Exception as e:
        if DEBUG: print(f"⚠️ Error getting render folder path: {e}"); return None

def get_current_houdini_file():
    try:
        current_file = hou.hipFile.name()
        if current_file and current_file != "untitled.hip":
            return os.path.normpath(current_file)
    except: pass
    return None

def is_current_file(file_path):
    current = get_current_houdini_file()
    if not current or not file_path: return False
    return os.path.normpath(file_path) == current

def infer_shot(full_path):
    filename = os.path.basename(full_path)
    match = SHOT_RX.match(filename)
    if match:
        shot_name = match.group(1)
        shot_upper = shot_name.upper()
        if shot_upper.startswith('SH'):
            return 'Sh' + shot_upper[2:]
        return shot_name
    parts=os.path.normpath(full_path).split(os.sep)
    try:
        # Look for common shot patterns in path
        for i, part in enumerate(parts):
            if part in ["03_lighting", "02_animation", "01_modeling", "04_comp", "05_render"]:
                if len(parts) > i + 1:
                    folder_name = parts[i + 1]
                    if '.' not in folder_name:
                        return folder_name
    except ValueError: pass
    
    # Fallback: try to extract from filename
    filename = os.path.basename(full_path)
    name, ext = os.path.splitext(filename)
    
    # Look for shot patterns in filename (Sh001, SH002, shot_001, etc.)
    shot_match = re.search(r'(?:sh|shot)[-_]?(\d+)', name, re.IGNORECASE)
    if shot_match:
        return f"Sh{shot_match.group(1).zfill(3)}"
    
    # Look for any 3-digit number that might be a shot
    number_match = re.search(r'(\d{3,4})', name)
    if number_match:
        return f"Sh{number_match.group(1).zfill(3)}"
    
    # Last resort: use first part of filename (before any version info)
    clean_name = re.sub(r'[_-]v\d+.*$', '', name)  # Remove version info
    clean_name = re.sub(r'[_-].*$', '', clean_name)  # Remove everything after first separator
    if clean_name and len(clean_name) > 2:
        return clean_name[:10]  # Limit length
    
    return "Unknown"

def parse_ver(name):
    m=VER_RX.search(name)
    return f"v{int(m.group(1)):03d}" if m else ""

def increment_version_and_backup(current_filepath, note=""):
    try:
        if not current_filepath or not os.path.exists(current_filepath):
            return False, "", "File không tồn tại"
        dir_path = os.path.dirname(current_filepath)
        filename = os.path.basename(current_filepath)
        name, ext = os.path.splitext(filename)
        ver_match = VER_RX.search(name)
        if not ver_match:
            return False, "", "Không tìm thấy version number trong tên file"
        current_ver_num = int(ver_match.group(1))
        new_ver_num = current_ver_num + 1
        ver_pattern = ver_match.group(0)
        ver_start_pos = ver_match.start()
        ver_end_pos = ver_match.end()
        
        # Extract base name (everything before version)
        base_name = name[:ver_start_pos].rstrip('_-.')
        
        # Remove any description/note after version (everything after ver_end_pos)
        # This ensures old notes don't carry over to new version
        
        # Build new filename: base_name + new_version + (optional new note)
        new_ver_str = f"v{new_ver_num:03d}"
        new_filename = base_name
        
        # Add separator before version if base_name doesn't end with separator
        if new_filename and not new_filename[-1] in '_-.':
            new_filename += '_'
        
        new_filename += new_ver_str
        
        # Add new note if provided
        if note and note.strip():
            clean_note = re.sub(r'[^\w\s-]', '', note.strip())
            clean_note = re.sub(r'[\s]+', '_', clean_note)
            if clean_note:
                new_filename = f"{new_filename}_{clean_note}"
        new_filename = new_filename + ext
        new_filepath = os.path.join(dir_path, new_filename)
        vers_folder = os.path.join(dir_path, "Vers")
        if not os.path.exists(vers_folder): os.makedirs(vers_folder)
        backup_path = os.path.join(vers_folder, filename)
        if os.path.exists(backup_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name_only = os.path.splitext(filename)[0]
            backup_filename = f"{name_only}_{timestamp}{ext}"
            backup_path = os.path.join(vers_folder, backup_filename)
        hou.hipFile.save()
        shutil.copy2(current_filepath, backup_path)
        hou.hipFile.setName(new_filepath)
        hou.hipFile.save()
        try:
            if os.path.exists(current_filepath): os.remove(current_filepath)
        except Exception: pass
        message = f"✅ Saved as {os.path.basename(new_filepath)}\n📦 Old version moved to Vers/"
        if note and note.strip(): message += f"\n📝 Note: {note}"
        return True, new_filepath, message
    except Exception as e:
        error_msg = f"Lỗi khi save version: {str(e)}"
        return False, "", error_msg

def collect_files(base_dir, depth=1):
    if not os.path.isdir(base_dir): return []
    results=[]
    if depth<=1:
        for e in os.scandir(base_dir):
            if e.is_file() and os.path.splitext(e.name)[1].lower() in HOUDINI_EXTS:
                results.append(e.path)
        return results
    return results

def collect_asset_files(base_dir, asset_type=None, department=None, asset_name=None):
    """
    Collect asset files from 01_assets structure
    Args:
        base_dir: Project root directory
        asset_type: Asset type filter (_characters, _environments, _graphic, etc.)
        department: Department filter (01_modeling, 02_rigging, etc.)
        asset_name: Asset name filter (char_Gefula, etc.)
    Returns:
        List of (filepath, asset_name, department_name) tuples
    """
    if DEBUG: print(f"🔍 collect_asset_files called with:")
    if DEBUG: print(f"  base_dir: {base_dir}")
    if DEBUG: print(f"  asset_type: {asset_type}")
    if DEBUG: print(f"  department: {department}")
    if DEBUG: print(f"  asset_name: {asset_name}")
    if DEBUG: print(f"  HOUDINI_EXTS: {HOUDINI_EXTS}")
    
    if not os.path.isdir(base_dir):
        if DEBUG: print(f"❌ Base directory does not exist: {base_dir}")
        return []
    
    assets_dir = os.path.join(base_dir, "01_assets")
    if DEBUG: print(f"🔍 Looking for assets directory: {assets_dir}")
    if not os.path.isdir(assets_dir):
        if DEBUG: print(f"❌ Assets directory does not exist: {assets_dir}")
        return []
    
    if DEBUG: print(f"✅ Assets directory found: {assets_dir}")
    results = []
    
    try:
        # Scan asset types
        if DEBUG: print(f"🔍 Scanning asset types in: {assets_dir}")
        type_entries = list(os.scandir(assets_dir))
        if DEBUG: print(f"  Found {len(type_entries)} entries in assets directory")
        
        for type_entry in type_entries:
            if DEBUG: print(f"  Checking entry: {type_entry.name} (is_dir: {type_entry.is_dir()})")
            if not type_entry.is_dir() or type_entry.name.startswith('.'):
                if DEBUG: print(f"    Skipping (not dir or hidden): {type_entry.name}")
                continue
                
            # Filter by asset type if specified
            if asset_type and type_entry.name != asset_type:
                if DEBUG: print(f"    Skipping (asset type filter): {type_entry.name} != {asset_type}")
                continue
                
            if DEBUG: print(f"    ✅ Processing asset type: {type_entry.name}")
                
            # Scan assets within this type
            asset_entries = list(os.scandir(type_entry.path))
            if DEBUG: print(f"    Found {len(asset_entries)} asset entries in {type_entry.name}")
            
            for asset_entry in asset_entries:
                if DEBUG: print(f"      Checking asset: {asset_entry.name} (is_dir: {asset_entry.is_dir()})")
                if not asset_entry.is_dir() or asset_entry.name.startswith('.'):
                    if DEBUG: print(f"        Skipping (not dir or hidden): {asset_entry.name}")
                    continue
                    
                current_asset_name = asset_entry.name
                if DEBUG: print(f"        ✅ Processing asset: {current_asset_name}")
                
                # Filter by asset name if specified
                if asset_name and current_asset_name != asset_name:
                    if DEBUG: print(f"        Skipping (asset name filter): {current_asset_name} != {asset_name}")
                    continue
                
                # Scan departments within this asset
                dept_entries = list(os.scandir(asset_entry.path))
                if DEBUG: print(f"        Found {len(dept_entries)} department entries in {current_asset_name}")
                
                for dept_entry in dept_entries:
                    if DEBUG: print(f"          Checking department: {dept_entry.name} (is_dir: {dept_entry.is_dir()})")
                    if not dept_entry.is_dir() or dept_entry.name.startswith('.'):
                        if DEBUG: print(f"            Skipping (not dir or hidden): {dept_entry.name}")
                        continue
                        
                    # Filter by department if specified
                    if department and dept_entry.name != department:
                        if DEBUG: print(f"            Skipping (department filter): {dept_entry.name} != {department}")
                        continue
                        
                    dept_name = dept_entry.name
                    if DEBUG: print(f"            ✅ Processing department: {dept_name}")
                    
                    # Scan files in this department
                    file_entries = list(os.scandir(dept_entry.path))
                    if DEBUG: print(f"            Found {len(file_entries)} files in {dept_name}")
                    
                    for file_entry in file_entries:
                        if DEBUG: print(f"              Checking file: {file_entry.name} (is_file: {file_entry.is_file()})")
                        if (file_entry.is_file() and 
                            os.path.splitext(file_entry.name)[1].lower() in HOUDINI_EXTS):
                            if DEBUG: print(f"                ✅ Found Houdini file: {file_entry.name}")
                            results.append((file_entry.path, current_asset_name, dept_name))
                        else:
                            ext = os.path.splitext(file_entry.name)[1].lower()
                            if DEBUG: print(f"                Skipping (not Houdini file): {file_entry.name} (ext: {ext})")
                            
    except Exception as e:
        if DEBUG: print(f"⚠️ Error collecting asset files: {e}")
        
    if DEBUG: print(f"🎯 Final result: Found {len(results)} asset files")
    for i, (filepath, asset_name, dept_name) in enumerate(results):
        if DEBUG: print(f"  {i+1}. {os.path.basename(filepath)} (asset: {asset_name}, dept: {dept_name})")
        
    return results

def list_asset_types(base_dir):
    """List available asset types in 01_assets directory"""
    if not os.path.isdir(base_dir):
        return []
    
    assets_dir = os.path.join(base_dir, "01_assets")
    if not os.path.isdir(assets_dir):
        return []
    
    types = []
    try:
        for entry in os.scandir(assets_dir):
            if entry.is_dir() and not entry.name.startswith('.'):
                types.append(entry.name)
        types.sort()
    except Exception as e:
        if DEBUG: print(f"⚠️ Error listing asset types: {e}")
    
    return types

def list_asset_names(base_dir, asset_type):
    """List available asset names for a specific asset type"""
    if not base_dir or not asset_type:
        return []
    
    type_dir = os.path.join(base_dir, "01_assets", asset_type)
    if not os.path.isdir(type_dir):
        return []
    
    assets = []
    try:
        for entry in os.scandir(type_dir):
            if entry.is_dir() and not entry.name.startswith('.'):
                assets.append(entry.name)
        assets.sort()
    except Exception as e:
        if DEBUG: print(f"⚠️ Error listing asset names: {e}")
    
    return assets

def list_departments(base_dir, asset_type, asset_name):
    """List available departments for a specific asset"""
    if not base_dir or not asset_type or not asset_name:
        return []
    
    asset_dir = os.path.join(base_dir, "01_assets", asset_type, asset_name)
    if not os.path.isdir(asset_dir):
        return []
    
    departments = []
    try:
        for entry in os.scandir(asset_dir):
            if entry.is_dir() and not entry.name.startswith('.'):
                departments.append(entry.name)
        departments.sort()
    except Exception as e:
        if DEBUG: print(f"⚠️ Error listing departments: {e}")
    
    return departments

def infer_asset_name(full_path):
    """Extract asset name from file path"""
    try:
        parts = os.path.normpath(full_path).split(os.sep)
        
        # Look for 01_assets in path
        if "01_assets" in parts:
            assets_idx = parts.index("01_assets")
            if len(parts) > assets_idx + 2:  # 01_assets/<type>/<asset>
                return parts[assets_idx + 2]
        
        # Fallback: use filename
        filename = os.path.basename(full_path)
        name, ext = os.path.splitext(filename)
        return name
        
    except Exception as e:
        if DEBUG: print(f"⚠️ Error inferring asset name: {e}")
        return "Unknown"

def infer_department(full_path):
    """Extract department from file path"""
    try:
        parts = os.path.normpath(full_path).split(os.sep)
        
        # Look for department pattern (01_modeling, 02_rigging, etc.)
        for part in parts:
            if re.match(r'\d{2}_\w+', part):
                return part
        
        # Fallback: use parent directory name
        parent_dir = os.path.basename(os.path.dirname(full_path))
        if parent_dir and parent_dir != "01_assets":
            return parent_dir
            
        return "Unknown"
        
    except Exception as e:
        if DEBUG: print(f"⚠️ Error inferring department: {e}")
        return "Unknown"

# ---------- Project root & tabs helpers ----------
DEFAULT_ROOT = r"D:\\Dropbox\\Job"

def list_projects(root_dir):
    projects=[]
    try:
        if not os.path.isdir(root_dir): return []
        for entry in os.scandir(root_dir):
            if entry.is_dir() and not entry.name.startswith('.'):
                projects.append(entry.name)
        projects.sort(key=lambda n: n.lower())
    except Exception as e:
        if DEBUG: print(f"⚠️ list_projects error: {e}")
    return projects

def load_tabs_settings(settings: 'QtCore.QSettings'):
    try:
        raw = settings.value("tabs_v2", "", type=str)
        if not raw:
            return [{"name": "lighting", "subpath": SUBPATH, "depth": 1}]
        data = json.loads(raw)
        if isinstance(data, list) and data:
            # sanitize entries
            clean=[]
            for it in data:
                name = str(it.get("name", "lighting"))
                subpath = str(it.get("subpath", SUBPATH))
                depth = int(it.get("depth", 1))
                clean.append({"name": name, "subpath": subpath, "depth": depth})
            return clean
    except Exception as e:
        if DEBUG: print(f"⚠️ load_tabs_settings error: {e}")
    return [{"name": "lighting", "subpath": SUBPATH, "depth": 1}]

def save_tabs_settings(settings: 'QtCore.QSettings', tabs_conf):
    try:
        settings.setValue("tabs_v2", json.dumps(tabs_conf))
        settings.sync()
    except Exception as e:
        if DEBUG: print(f"⚠️ save_tabs_settings error: {e}")


def clean_type_name(type_name):
    """
    Clean type name: remove underscore prefix
    Examples: _characters → characters, _environments → environments
    """
    if not type_name:
        return ""
    return type_name.lstrip('_')

def clean_department_name(dept_name):
    """
    Clean department name: remove number prefix and underscore
    Examples: 01_modeling → modeling, 02_rigging → rigging
    """
    if not dept_name:
        return ""
    # Remove pattern like "01_", "02_", etc.
    cleaned = re.sub(r'^\d+_', '', dept_name)
    return cleaned

def clean_asset_name(asset_name):
    """
    Clean asset name: remove prefix like char_, prop_, env_
    Examples: char_Cyborg → Cyborg, prop_Chair → Chair
    """
    if not asset_name:
        return ""
    # Remove common prefixes
    prefixes = ['char_', 'prop_', 'env_', 'veh_', 'fx_', 'graphic_']
    for prefix in prefixes:
        if asset_name.lower().startswith(prefix):
            return asset_name[len(prefix):]
    return asset_name

def get_standard_departments():
    """
    Get standard department list for asset creation
    Loads from config/department_structure.json or returns defaults
    """
    try:
        # Try to load from config file
        import sys
        from pathlib import Path
        
        # Find config file relative to this module
        current_dir = Path(__file__).parent.parent.parent
        config_file = current_dir / "config" / "department_structure.json"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                departments = config.get('standard_departments', [])
                # Return just the IDs
                return [dept['id'] for dept in departments]
    except Exception as e:
        if DEBUG:
            debug_print(f"⚠️ Could not load department config: {e}")
    
    # Fallback to hardcoded defaults
    return [
        "01_modeling",
        "02_rigging",
        "03_surfacing",
        "04_lookdev",
        "05_groom",
        "06_anim",
        "07_turntable",
    ]

def load_department_config():
    """Load full department configuration"""
    try:
        from pathlib import Path
        current_dir = Path(__file__).parent.parent.parent
        config_file = current_dir / "config" / "department_structure.json"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        if DEBUG:
            debug_print(f"⚠️ Could not load department config: {e}")
    
    return None

def save_department_config(config_data):
    """Save department configuration"""
    try:
        from pathlib import Path
        current_dir = Path(__file__).parent.parent.parent
        config_file = current_dir / "config" / "department_structure.json"
        
        # Ensure config directory exists
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        return True, "Configuration saved successfully!"
    except Exception as e:
        return False, f"Failed to save configuration:\n{str(e)}"

def load_asset_types_config():
    """
    Load asset types from config
    Returns list of types that can be created (even if folders don't exist yet)
    """
    try:
        config = load_department_config()
        if config and 'asset_types' in config:
            return config['asset_types']
    except Exception as e:
        if DEBUG:
            debug_print(f"⚠️ Could not load asset types: {e}")
    
    # Fallback defaults
    return [
        {"id": "_characters", "name": "Characters", "prefix": "char_", "icon": "🧑"},
        {"id": "_props", "name": "Props", "prefix": "prop_", "icon": "📦"},
        {"id": "_environments", "name": "Environments", "prefix": "env_", "icon": "🏞️"},
    ]

def get_asset_prefix(type_name, asset_name=None):
    """
    Get asset prefix for a given type name.
    Centralized logic - used by all file/folder creation functions.
    
    Args:
        type_name: Asset type like "_characters"
        asset_name: Optional asset name to check if prefix already exists
    
    Returns:
        Prefix string like "char_" or empty string
    """
    # Check if asset_name already has prefix
    if asset_name:
        prefixes = ['char_', 'prop_', 'env_', 'veh_', 'fx_', 'weap_', 'set_', 'cam_', 'light_']
        for prefix in prefixes:
            if asset_name.lower().startswith(prefix):
                return ''  # Already has prefix
    
    # Try to get prefix from asset types config
    asset_types = load_asset_types_config()
    for atype in asset_types:
        if atype['id'] == type_name:
            prefix = atype.get('prefix', '')
            if prefix:
                return prefix
    
    # Fallback to guessing (should rarely happen if config is correct)
    type_lower = type_name.lower()
    if 'character' in type_lower:
        return 'char_'
    elif 'prop' in type_lower:
        return 'prop_'
    elif 'environment' in type_lower:
        return 'env_'
    elif 'vehicle' in type_lower:
        return 'veh_'
    elif 'weapon' in type_lower:
        return 'weap_'
    elif 'fx' in type_lower or 'effect' in type_lower:
        return 'fx_'
    else:
        return ''


def ensure_asset_name_has_prefix(type_name, asset_name):
    """
    Ensure asset name has correct prefix based on type.
    
    Args:
        type_name: Asset type like "_characters"
        asset_name: Asset name like "Cyborg" or "char_Cyborg"
    
    Returns:
        Asset name with prefix: "char_Cyborg"
    """
    prefix = get_asset_prefix(type_name, asset_name)
    if prefix and not asset_name.lower().startswith(prefix):
        return f"{prefix}{asset_name}"
    return asset_name


def build_file_directory_path(root, project, type_name, asset_name, department, 
                               subdepartment=None, username=None, is_assets=True):
    """
    Build the directory path where a file should be created.
    Centralized path building logic - used by dialogs and creation functions.
    
    Args:
        root: Project root directory
        project: Project name
        type_name: Type like "_characters" or "Shots"
        asset_name: Asset name like "char_Cyborg" (should already have prefix)
        department: Department like "01_modeling"
        subdepartment: Optional subdepartment like "01_sculpt"
        username: Optional username for user workspace
        is_assets: True for assets, False for shots
    
    Returns:
        Full directory path (absolute)
    """
    if is_assets:
        # Assets: 01_assets/_characters/char_Cyborg/01_modeling/[01_sculpt/]username/
        path_parts = [root, project, "01_assets", type_name, asset_name, department]
    else:
        # Shots: 02_shots/department/[subdept/]username/
        path_parts = [root, project, "02_shots", department]
    
    if subdepartment:
        path_parts.append(subdepartment)
    
    if username:
        path_parts.append(username)
    
    return os.path.join(*path_parts)


def build_file_preview_path(type_name, asset_name, department, subdepartment=None, 
                           username=None, is_assets=True, filename=None):
    """
    Build relative path for preview in dialogs.
    Uses same logic as build_file_directory_path but returns relative path.
    
    Args:
        type_name: Type like "_characters" or "Shots"
        asset_name: Asset name like "char_Cyborg"
        department: Department like "01_modeling"
        subdepartment: Optional subdepartment
        username: Optional username
        is_assets: True for assets, False for shots
        filename: Optional filename to append
    
    Returns:
        Relative path string for display
    """
    if is_assets:
        path_parts = ["01_assets", type_name, asset_name, department]
    else:
        path_parts = ["02_shots", department]
    
    if subdepartment:
        path_parts.append(subdepartment)
    
    if username:
        path_parts.append(username)
    
    if filename:
        path_parts.append(filename)
    
    return os.path.join(*path_parts)


def create_shot_folder_structure(base_dir, shot_name, departments=None):
    """
    Create complete folder structure for a new shot.
    Similar to create_asset_folder_structure but for shots.
    
    Args:
        base_dir: Project root directory
        shot_name: Shot name like "sq010_sh0010"
        departments: List of department configs (None = use standard from config)
    
    Returns:
        (success, shot_folder_path, message)
    """
    try:
        # Ensure parent folders exist
        shots_dir = os.path.join(base_dir, "02_shots")
        os.makedirs(shots_dir, exist_ok=True)
        
        # Create shot folder
        shot_folder = os.path.join(shots_dir, shot_name)
        
        if os.path.exists(shot_folder):
            return False, shot_folder, f"Shot folder already exists:\n{shot_folder}"
        
        # Load shot departments if not provided
        if not departments:
            config = load_department_config()
            if config and 'shot_departments' in config:
                departments = config['shot_departments']
            else:
                return False, "", "No shot departments configured"
        
        # Create all department folders with subdepartments
        created_structure = []
        for dept in departments:
            dept_id = dept['id']
            dept_folder = os.path.join(shot_folder, dept_id)
            os.makedirs(dept_folder, exist_ok=True)
            created_structure.append(dept_id)
            
            # Create subdepartments
            for subdept in dept.get('subdepartments', []):
                subdept_id = subdept['id']
                subdept_folder = os.path.join(dept_folder, subdept_id)
                os.makedirs(subdept_folder, exist_ok=True)
                created_structure.append(f"{dept_id}/{subdept_id}")
                
                # Subdepartment publish folder
                if subdept.get('create_publish', False):
                    subdept_publish = os.path.join(subdept_folder, '_publish')
                    os.makedirs(subdept_publish, exist_ok=True)
                    created_structure.append(f"{dept_id}/{subdept_id}/_publish")
            
            # Software subfolders
            for sw in dept.get('software_folders', []):
                sw_folder = os.path.join(dept_folder, sw)
                os.makedirs(sw_folder, exist_ok=True)
                created_structure.append(f"{dept_id}/{sw}")
            
            # Department publish folder
            if dept.get('create_publish', False):
                publish_folder = os.path.join(dept_folder, '_publish')
                os.makedirs(publish_folder, exist_ok=True)
                created_structure.append(f"{dept_id}/_publish")
        
        # Build success message
        success_msg = f"Shot folder created successfully!\n\n"
        success_msg += f"Shot: {shot_name}\n"
        success_msg += f"Location: {shot_folder}\n\n"
        success_msg += f"Structure created:\n"
        for item in created_structure:
            if '/' in item:
                dept, sub = item.split('/', 1)
                success_msg += f"  {dept}/\n    └─ {sub}/\n"
            else:
                success_msg += f"  {item}/\n"
        
        return True, shot_folder, success_msg
        
    except Exception as e:
        return False, "", f"Failed to create shot folder:\n{str(e)}"


def create_asset_folder_structure(base_dir, type_name, asset_name, departments=None):
    """
    Create complete folder structure for a new asset with software subfolders
    
    Args:
        base_dir: Project root directory
        type_name: Asset type like "_characters"
        asset_name: Asset name like "char_Cyborg" (with prefix) or "Cyborg" (auto-prefix)
        departments: List of department folders to create (None = use standard)
    
    Returns:
        (success, asset_folder_path, message)
    """
    try:
        # Use centralized prefix helper
        asset_name = ensure_asset_name_has_prefix(type_name, asset_name)
        
        # Ensure parent folders exist
        assets_dir = os.path.join(base_dir, "01_assets")
        os.makedirs(assets_dir, exist_ok=True)
        
        type_dir = os.path.join(assets_dir, type_name)
        os.makedirs(type_dir, exist_ok=True)
        
        # Create asset folder
        asset_folder = os.path.join(type_dir, asset_name)
        
        if os.path.exists(asset_folder):
            return False, asset_folder, f"Asset folder already exists:\n{asset_folder}"
        
        # Use standard departments if not specified
        if not departments:
            departments = get_standard_departments()
        
        # Load department config for software subfolders
        config = load_department_config()
        dept_map = {}
        if config and 'standard_departments' in config:
            dept_map = {d['id']: d for d in config['standard_departments']}
        
        # Create all department folders (with software subfolders + subdepartments + publish)
        created_structure = []
        for dept_id in departments:
            dept_path = os.path.join(asset_folder, dept_id)
            
            # Get department config
            dept_config = dept_map.get(dept_id, {})
            software_folders = dept_config.get('software_folders', [])
            create_publish = dept_config.get('create_publish', False)
            subdepartments = dept_config.get('subdepartments', [])
            
            if software_folders:
                # Create software subfolders
                for software in software_folders:
                    software_path = os.path.join(dept_path, software)
                    os.makedirs(software_path, exist_ok=True)
                    created_structure.append(f"{dept_id}/{software}")
                
                # Create subdepartments
                for subdept in subdepartments:
                    subdept_id = subdept['id']
                    subdept_path = os.path.join(dept_path, subdept_id)
                    os.makedirs(subdept_path, exist_ok=True)
                    created_structure.append(f"{dept_id}/{subdept_id}")
                    
                    # Subdepartment publish folder
                    if subdept.get('create_publish', False):
                        subdept_publish = os.path.join(subdept_path, "_publish")
                        os.makedirs(subdept_publish, exist_ok=True)
                        created_structure.append(f"{dept_id}/{subdept_id}/_publish")
                
                # Also create publish folder at department level
                if create_publish:
                    publish_path = os.path.join(dept_path, "_publish")
                    os.makedirs(publish_path, exist_ok=True)
                    created_structure.append(f"{dept_id}/_publish")
            else:
                # Just create department folder
                os.makedirs(dept_path, exist_ok=True)
                created_structure.append(dept_id)
                
                # Create subdepartments
                for subdept in subdepartments:
                    subdept_id = subdept['id']
                    subdept_path = os.path.join(dept_path, subdept_id)
                    os.makedirs(subdept_path, exist_ok=True)
                    created_structure.append(f"{dept_id}/{subdept_id}")
                    
                    # Subdepartment publish folder
                    if subdept.get('create_publish', False):
                        subdept_publish = os.path.join(subdept_path, "_publish")
                        os.makedirs(subdept_publish, exist_ok=True)
                        created_structure.append(f"{dept_id}/{subdept_id}/_publish")
                
                # Create publish subfolder if configured
                if create_publish:
                    publish_path = os.path.join(dept_path, "_publish")
                    os.makedirs(publish_path, exist_ok=True)
                    created_structure.append(f"{dept_id}/_publish")
        
        # Build success message with structure details
        success_msg = f"Asset folder created successfully!\n\n"
        success_msg += f"Asset: {asset_name}\n"
        success_msg += f"Type: {type_name}\n"
        success_msg += f"Location: {asset_folder}\n\n"
        success_msg += f"Structure created:\n"
        
        current_dept = None
        for item in created_structure:
            if '/' in item:
                # Software subfolder
                dept, software = item.split('/')
                if dept != current_dept:
                    success_msg += f"  {dept}/\n"
                    current_dept = dept
                success_msg += f"    ├─ {software}/\n"
            else:
                # Simple department
                success_msg += f"  {item}/\n"
                current_dept = item
        
        return True, asset_folder, success_msg
        
    except Exception as e:
        return False, "", f"Failed to create asset folder:\n{str(e)}"

def generate_new_filename(type_name, asset_name, department, version="v001", ext=".hip", subdepartment=None):
    """
    Generate filename in format: $type_$assetname_$department_$version.ext
    
    Args:
        type_name: Type like "_characters" → "characters"
        asset_name: Asset like "char_Cyborg" → "Cyborg"
        department: Department like "01_modeling" → "modeling"
        version: Version string like "v001"
        ext: File extension like ".hip"
        subdepartment: Optional subdepartment like "01_sculpt" → "sculpt"
                        If provided, uses subdepartment name instead of department name
    
    Returns:
        Filename like "characters_Cyborg_modeling_v001.hip"
        Or "characters_Cyborg_sculpt_v001.hip" if subdepartment is provided
    """
    clean_type = clean_type_name(type_name)
    clean_asset = clean_asset_name(asset_name)
    
    # Use subdepartment name if provided, otherwise use department name
    if subdepartment:
        clean_dept = clean_department_name(subdepartment)
    else:
        clean_dept = clean_department_name(department)
    
    # Ensure version has 'v' prefix
    if not version.startswith('v'):
        version = f"v{version}"
    
    # Ensure extension has dot
    if not ext.startswith('.'):
        ext = f".{ext}"
    
    filename = f"{clean_type}_{clean_asset}_{clean_dept}_{version}{ext}"
    return filename

def parse_asset_info_from_filename(filename):
    """
    Parse asset type, asset name, department from filename
    Examples:
    - char_Gefula_modeling_v001.hip -> (_characters, char_Gefula, 01_modeling)
    - env_Forest_lighting_v002.hip -> (_environments, env_Forest, 03_lighting)
    - prop_Chair_surfacing_v003.hip -> (_props, prop_Chair, 03_surfacing)
    """
    try:
        # Remove extension
        name_no_ext = os.path.splitext(filename)[0]
        
        # Common patterns for asset types
        asset_type_patterns = {
            r'^char_': '_characters',
            r'^env_': '_environments', 
            r'^prop_': '_props',
            r'^veh_': '_vehicles',
            r'^fx_': '_effects',
            r'^graphic_': '_graphic'
        }
        
        # Common patterns for departments
        dept_patterns = {
            r'modeling': '01_modeling',
            r'rigging': '02_rigging', 
            r'surfacing': '03_surfacing',
            r'lookdev': '04_lookdev',
            r'groom': '05_groom',
            r'anim': '06_anim',
            r'cloth': '06_cloth',
            r'lighting': '03_lighting',
            r'comp': '04_comp'
        }
        
        # Extract asset type
        asset_type = None
        for pattern, type_name in asset_type_patterns.items():
            if re.search(pattern, name_no_ext, re.IGNORECASE):
                asset_type = type_name
                break
        
        # Extract department
        department = None
        for pattern, dept_name in dept_patterns.items():
            if re.search(pattern, name_no_ext, re.IGNORECASE):
                department = dept_name
                break
        
        # Extract asset name (everything before department)
        asset_name = None
        if department:
            # Remove version and department info to get asset name
            clean_name = re.sub(r'_v\d+$', '', name_no_ext)  # Remove version
            clean_name = re.sub(r'_(modeling|rigging|surfacing|lookdev|groom|anim|cloth|lighting|comp)$', '', clean_name, flags=re.IGNORECASE)
            asset_name = clean_name
        else:
            # If no department found, use the whole name (minus version)
            asset_name = re.sub(r'_v\d+$', '', name_no_ext)
        
        return asset_type, asset_name, department
        
    except Exception as e:
        if DEBUG: print(f"⚠️ Error parsing asset info from filename '{filename}': {e}")
        return None, None, None


def collect_asset_files_filename(base_dir, asset_type=None, department=None, asset_name=None):
    """
    Collect asset files by scanning all .hip files and parsing filenames
    This is a fallback method when subfolder structure is not available
    """
    if DEBUG: print(f"🔍 collect_asset_files_filename called with:")
    if DEBUG: print(f"  base_dir: {base_dir}")
    if DEBUG: print(f"  asset_type: {asset_type}")
    if DEBUG: print(f"  department: {department}")
    if DEBUG: print(f"  asset_name: {asset_name}")
    
    if not os.path.isdir(base_dir):
        if DEBUG: print(f"❌ Base directory does not exist: {base_dir}")
        return []
    
    results = []
    
    try:
        # Scan for all .hip files recursively
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if os.path.splitext(file)[1].lower() in HOUDINI_EXTS:
                    filepath = os.path.join(root, file)
                    
                    # Parse asset info from filename
                    parsed_type, parsed_asset, parsed_dept = parse_asset_info_from_filename(file)
                    
                    if not parsed_asset:  # Skip if we can't parse asset name
                        continue
                    
                    # Apply filters
                    if asset_type and parsed_type != asset_type:
                        continue
                    if department and parsed_dept != department:
                        continue
                    if asset_name and parsed_asset != asset_name:
                        continue
                    
                    results.append((filepath, parsed_asset, parsed_dept or "unknown"))
                    if DEBUG: print(f"  ✅ Found: {file} -> asset: {parsed_asset}, dept: {parsed_dept or 'unknown'}")
    
    except Exception as e:
        if DEBUG: print(f"⚠️ Error in filename-based collection: {e}")
    
    if DEBUG: print(f"🎯 Filename-based result: Found {len(results)} asset files")
    return results


def collect_asset_files_hybrid(base_dir, asset_type=None, department=None, asset_name=None):
    """
    Hybrid approach: try subfolder-based search first, then filename-based search
    """
    if DEBUG: print(f"🔄 Starting hybrid asset collection")
    
    # First try subfolder-based search
    if DEBUG: print("1️⃣ Trying subfolder-based search...")
    subfolder_results = collect_asset_files(base_dir, asset_type, department, asset_name)
    
    if subfolder_results:
        if DEBUG: print(f"✅ Subfolder-based search found {len(subfolder_results)} files")
        return subfolder_results
    
    # If no results, try filename-based search
    if DEBUG: print("2️⃣ No subfolder results, trying filename-based search...")
    filename_results = collect_asset_files_filename(base_dir, asset_type, department, asset_name)
    
    if filename_results:
        if DEBUG: print(f"✅ Filename-based search found {len(filename_results)} files")
    else:
        if DEBUG: print("❌ No files found with either method")
    
    return filename_results

# ================ NEW SCAN FUNCTIONS FOR SETTINGS DIALOG ================

IGNORE_FOLDERS = {'backup', 'Vers', 'old', '.git', '__pycache__', '_thumbnail'}

# ================ SUBDEPARTMENT & USER WORKSPACE PATTERNS ================

# Subdepartment pattern: \d{2}_[a-z][a-z0-9_]*
SUBDEPT_PATTERN = re.compile(r'^\d{2}_[a-z][a-z0-9_]*$')

# Reserved system folders
RESERVED_SYSTEM_FOLDERS = {'_publish', '_archive', '_thumbnail', 'Vers', 'backup'}

# User workspace pattern: lowercase alphanumeric + underscore (no \d{2}_ prefix)
USER_WORKSPACE_PATTERN = re.compile(r'^[a-z0-9_]+$')

def get_subdepartments_for_department(dept_id):
    """
    Get subdepartments from config for a specific department
    
    Args:
        dept_id: Department ID (e.g., "01_modeling", "02_sim")
    
    Returns:
        List of subdepartment dicts with 'id', 'name', 'create_publish'
    """
    config = load_department_config()
    if config:
        # Check standard departments (assets)
        if 'standard_departments' in config:
            for dept in config['standard_departments']:
                if dept['id'] == dept_id:
                    return dept.get('subdepartments', [])
        
        # Check shot departments
        if 'shot_departments' in config:
            for dept in config['shot_departments']:
                if dept['id'] == dept_id:
                    return dept.get('subdepartments', [])
    
    return []


def get_subdepartments_with_metadata(base_dir, type_name, dept_id, is_assets=True):
    """
    Get subdepartments with metadata: scan from folders + merge with config
    
    Args:
        base_dir: Project root directory
        type_name: Type name (e.g., "_characters", "Shots")
        dept_id: Department ID (e.g., "01_modeling", "02_sim")
        is_assets: Whether this is an assets type or shots type
    
    Returns:
        List of subdepartment dicts with 'id', 'name', 'from_config'
    """
    # 1. Get subdepartments from config
    subdepts_from_config = get_subdepartments_for_department(dept_id)
    config_map = {s['id']: s for s in subdepts_from_config}
    
    # 2. Scan subdepartments from actual folders
    actual_subdepts = {}
    
    try:
        if is_assets:
            # For assets: scan type/asset_name/dept_id/ for subdepartments
            type_dir = os.path.join(base_dir, "01_assets", type_name)
            if os.path.isdir(type_dir):
                # Scan all assets in this type
                for asset_entry in os.scandir(type_dir):
                    if (asset_entry.is_dir() and 
                        not asset_entry.name.startswith('.') and 
                        asset_entry.name not in IGNORE_FOLDERS):
                        dept_folder = os.path.join(asset_entry.path, dept_id)
                        if os.path.isdir(dept_folder):
                            # Scan subdepartments in this department
                            for entry in os.scandir(dept_folder):
                                if entry.is_dir():
                                    pattern_match = SUBDEPT_PATTERN.match(entry.name)
                                    is_reserved = entry.name in RESERVED_SYSTEM_FOLDERS
                                    is_hidden = entry.name.startswith('.')
                                    
                                    if (not is_hidden and 
                                        not is_reserved and
                                        pattern_match):
                                        # Found actual subdepartment folder
                                        if entry.name not in actual_subdepts:
                                            actual_subdepts[entry.name] = {
                                                'id': entry.name,
                                                'name': entry.name.split('_')[-1].capitalize(),
                                                'from_config': False
                                            }
        else:
            # For shots: scan 02_shots/dept_id/ for subdepartments
            shots_dir = os.path.join(base_dir, "02_shots")
            dept_folder = os.path.join(shots_dir, dept_id)
            if os.path.isdir(dept_folder):
                for entry in os.scandir(dept_folder):
                    if entry.is_dir():
                        pattern_match = SUBDEPT_PATTERN.match(entry.name)
                        is_reserved = entry.name in RESERVED_SYSTEM_FOLDERS
                        is_hidden = entry.name.startswith('.')
                        
                        if (not is_hidden and 
                            not is_reserved and
                            pattern_match):
                            if entry.name not in actual_subdepts:
                                actual_subdepts[entry.name] = {
                                    'id': entry.name,
                                    'name': entry.name.split('_')[-1].capitalize(),
                                    'from_config': False
                                }
    except Exception as e:
        if DEBUG:
            debug_print(f"⚠️ Error scanning subdepartments: {e}")
    
    # 3. Merge: actual folders + config (config has priority for name)
    merged_subdepts = {}
    
    # First, add actual folders found
    for subdept_id, subdept_info in actual_subdepts.items():
        merged_subdepts[subdept_id] = subdept_info
    
    # Then, add/update from config (config has priority for name)
    for subdept in subdepts_from_config:
        subdept_id = subdept['id']
        merged_subdepts[subdept_id] = {
            'id': subdept_id,
            'name': subdept.get('name', subdept_id.split('_')[-1].capitalize()),
            'from_config': True
        }
    
    # Sort by ID
    return sorted(merged_subdepts.values(), key=lambda x: x['id'])

def is_subdepartment_folder(folder_name, dept_id):
    """
    Check if folder is a valid subdepartment (not user folder)
    
    Args:
        folder_name: Folder name to check
        dept_id: Parent department ID
    
    Returns:
        bool: True if it's a subdepartment, False if user folder
    """
    # Pattern check: Must be \d{2}_name
    if not SUBDEPT_PATTERN.match(folder_name):
        return False  # Not subdepartment format -> user folder
    
    # Config check: Must exist in config
    subdepts = get_subdepartments_for_department(dept_id)
    return folder_name in [s['id'] for s in subdepts]

def is_user_workspace(folder_name):
    """
    Check if folder is a user workspace
    
    Rules:
    - Lowercase alphanumeric + underscore
    - MUST start with lowercase letter (not underscore, not number)
    - NOT matching subdepartment pattern (\d{2}_)
    - NOT reserved system folders
    - NOT starting with underscore (system folders)
    
    Returns:
        bool: True if it's a user workspace folder
    """
    # Reserved system folders
    if folder_name in RESERVED_SYSTEM_FOLDERS:
        return False
    
    # Folders starting with underscore are system/reserved folders
    if folder_name.startswith('_'):
        return False
    
    # Subdepartment pattern (numeric prefix)
    if re.match(r'^\d{2}_', folder_name):
        return False
    
    # User workspace pattern - must start with lowercase letter
    # Pattern: ^[a-z][a-z0-9_]*$ (starts with letter, then alphanumeric + underscore)
    if re.match(r'^[a-z][a-z0-9_]*$', folder_name):
        return True
    
    return False


def scan_user_workspaces_in_path(base_dir, type_name, asset_name, department, subdepartment=None, is_assets=True):
    """
    Scan for user workspace folders in department/subdepartment path
    
    Args:
        base_dir: Project root directory
        type_name: Type name (e.g., "_characters", "Shots")
        asset_name: Asset name (for assets only)
        department: Department ID (e.g., "01_modeling")
        subdepartment: Optional subdepartment ID (e.g., "01_sculpt")
        is_assets: True for assets, False for shots
    
    Returns:
        List of user workspace folder names found (sorted)
    """
    if not base_dir or not department:
        return []
    
    user_folders = set()
    
    try:
        if is_assets:
            # For assets: scan type/asset_name/department/[subdept/] for user folders
            if not type_name or not asset_name:
                return []
            
            type_dir = os.path.join(base_dir, "01_assets", type_name)
            if not os.path.isdir(type_dir):
                return []
            
            asset_dir = os.path.join(type_dir, asset_name)
            if not os.path.isdir(asset_dir):
                return []
            
            dept_dir = os.path.join(asset_dir, department)
            if not os.path.isdir(dept_dir):
                return []
            
            # If subdepartment specified, scan in subdept folder
            if subdepartment:
                subdept_dir = os.path.join(dept_dir, subdepartment)
                if os.path.isdir(subdept_dir):
                    for entry in os.scandir(subdept_dir):
                        if entry.is_dir() and is_user_workspace(entry.name):
                            user_folders.add(entry.name)
            else:
                # Scan in department folder (not in subdept)
                for entry in os.scandir(dept_dir):
                    if entry.is_dir() and is_user_workspace(entry.name):
                        user_folders.add(entry.name)
        else:
            # For shots: scan 02_shots/department/[subdept/] for user folders
            shots_dir = os.path.join(base_dir, "02_shots")
            if not os.path.isdir(shots_dir):
                return []
            
            dept_dir = os.path.join(shots_dir, department)
            if not os.path.isdir(dept_dir):
                return []
            
            # If subdepartment specified, scan in subdept folder
            if subdepartment:
                subdept_dir = os.path.join(dept_dir, subdepartment)
                if os.path.isdir(subdept_dir):
                    for entry in os.scandir(subdept_dir):
                        if entry.is_dir() and is_user_workspace(entry.name):
                            user_folders.add(entry.name)
            else:
                # Scan in department folder (not in subdept)
                for entry in os.scandir(dept_dir):
                    if entry.is_dir() and is_user_workspace(entry.name):
                        user_folders.add(entry.name)
    
    except Exception as e:
        if DEBUG:
            debug_print(f"⚠️ Error scanning user workspaces: {e}")
    
    return sorted(list(user_folders))

def validate_username(username):
    """
    Validate username format
    
    Returns:
        (bool, str): (is_valid, error_message)
    """
    if not username:
        return False, "Username cannot be empty"
    
    # Must be lowercase alphanumeric + underscore
    if not USER_WORKSPACE_PATTERN.match(username):
        return False, "Username must be lowercase letters, numbers, underscore only"
    
    # Cannot start with numbers (reserved for subdepartments)
    if re.match(r'^\d{2}_', username):
        return False, "Username cannot start with ## pattern (reserved)"
    
    # Max length
    if len(username) > 20:
        return False, "Username too long (max 20 characters)"
    
    return True, ""

def get_current_username():
    """
    Get current username (auto-detect or from settings)
    Returns: lowercase username
    """
    import getpass
    
    # Try to get from settings first
    s = QtCore.QSettings(ORG, APP)
    custom_username = s.value("user_name", "", type=str)
    
    if custom_username:
        return custom_username.lower()
    
    # Auto-detect from OS
    try:
        os_username = getpass.getuser()
        return os_username.lower().replace(' ', '_').replace('-', '_')
    except:
        return "user"

def get_user_metadata_path(project_root):
    """Get path to user metadata file"""
    return os.path.join(project_root, ".mono", "users.json")

def load_user_metadata(project_root):
    """
    Load user metadata from project
    
    Returns:
        dict: User metadata or empty dict
    """
    metadata_path = get_user_metadata_path(project_root)
    
    if not os.path.exists(metadata_path):
        return {"users": {}, "version": "1.0"}
    
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        if DEBUG:
            debug_print(f"⚠️ Error loading user metadata: {e}")
        return {"users": {}, "version": "1.0"}

def save_user_metadata(project_root, metadata):
    """Save user metadata to project"""
    metadata_path = get_user_metadata_path(project_root)
    
    try:
        # Create .mono directory if not exists
        os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        if DEBUG:
            debug_print(f"⚠️ Error saving user metadata: {e}")
        return False

def register_user_activity(project_root, username, full_name=None, email=None, department=None):
    """
    Register or update user activity in metadata
    
    Args:
        project_root: Project root directory
        username: Username (lowercase)
        full_name: Optional full name
        email: Optional email
        department: Optional department
    """
    from datetime import datetime
    
    metadata = load_user_metadata(project_root)
    
    if username not in metadata["users"]:
        # New user - register
        metadata["users"][username] = {
            "full_name": full_name or username,
            "email": email or "",
            "department": department or "",
            "created": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat()
        }
        if DEBUG:
            debug_print(f"📝 Registered new user: {username}")
    else:
        # Existing user - update activity
        metadata["users"][username]["last_active"] = datetime.now().isoformat()
        
        # Update info if provided
        if full_name:
            metadata["users"][username]["full_name"] = full_name
        if email:
            metadata["users"][username]["email"] = email
        if department:
            metadata["users"][username]["department"] = department
    
    save_user_metadata(project_root, metadata)

def scan_project_types(base_dir):
    """
    Scan project directory for available types
    Returns: List of (type_name, type_path, is_assets) tuples
    """
    if not os.path.isdir(base_dir):
        return []
    
    types = []
    
    try:
        # Scan 01_assets/ for _* folders
        assets_dir = os.path.join(base_dir, "01_assets")
        if os.path.isdir(assets_dir):
            for entry in os.scandir(assets_dir):
                if (entry.is_dir() and 
                    not entry.name.startswith('.') and 
                    entry.name not in IGNORE_FOLDERS and
                    entry.name.startswith('_')):
                    types.append((entry.name, entry.path, True))  # (name, path, is_assets)
        
        # Add 02_shots/ as a single type
        shots_dir = os.path.join(base_dir, "02_shots")
        if os.path.isdir(shots_dir):
            types.append(("Shots", shots_dir, False))  # (name, path, is_assets)
            
    except Exception as e:
        if DEBUG: print(f"⚠️ Error scanning project types: {e}")
    
    # Sort: assets first (alphabetically), then shots
    types.sort(key=lambda x: (not x[2], x[0]))  # is_assets=False comes first for shots
    return types

def scan_departments_for_type(base_dir, type_name, is_assets=True):
    """
    Scan departments for a specific type
    Args:
        base_dir: Project root directory
        type_name: Type name (e.g., "_characters", "Shots")
        is_assets: Whether this is an assets type or shots type
    Returns: List of department names
    """
    if not base_dir or not type_name:
        return []
    
    departments = set()
    
    try:
        if is_assets:
            # For assets: scan all asset_name/department combinations
            type_dir = os.path.join(base_dir, "01_assets", type_name)
            if os.path.isdir(type_dir):
                for asset_entry in os.scandir(type_dir):
                    if (asset_entry.is_dir() and 
                        not asset_entry.name.startswith('.') and 
                        asset_entry.name not in IGNORE_FOLDERS):
                        # Scan departments within this asset
                        for dept_entry in os.scandir(asset_entry.path):
                            if (dept_entry.is_dir() and 
                                not dept_entry.name.startswith('.') and 
                                dept_entry.name not in IGNORE_FOLDERS):
                                departments.add(dept_entry.name)
        else:
            # For shots: scan 02_shots/ for department folders
            shots_dir = os.path.join(base_dir, "02_shots")
            if os.path.isdir(shots_dir):
                for entry in os.scandir(shots_dir):
                    if (entry.is_dir() and 
                        not entry.name.startswith('.') and 
                        entry.name not in IGNORE_FOLDERS):
                        departments.add(entry.name)
                        
    except Exception as e:
        if DEBUG: print(f"⚠️ Error scanning departments for type '{type_name}': {e}")
    
    # Sort departments
    return sorted(list(departments))

def get_departments_with_metadata(base_dir, type_name, is_assets=True):
    """
    Get departments with metadata: scan from folders + merge with config
    
    Args:
        base_dir: Project root directory
        type_name: Type name (e.g., "_characters", "Shots")
        is_assets: Whether this is an assets type or shots type
    
    Returns:
        List of department dicts with 'id', 'name', 'icon', 'from_config'
        - 'from_config': True if department exists in config, False if scanned only
    """
    # 1. Scan departments from actual folders
    scanned_dept_ids = scan_departments_for_type(base_dir, type_name, is_assets)
    
    # 2. Load config for metadata
    config = load_department_config()
    dept_map = {}
    if config:
        if is_assets and 'standard_departments' in config:
            dept_map = {d['id']: d for d in config['standard_departments']}
        elif not is_assets and 'shot_departments' in config:
            dept_map = {d['id']: d for d in config['shot_departments']}
    
    # 3. Merge: scanned departments + config metadata
    departments = []
    for dept_id in scanned_dept_ids:
        dept_config = dept_map.get(dept_id, {})
        
        departments.append({
            'id': dept_id,
            'name': dept_config.get('name', dept_id),  # Use config name or fallback to ID
            'icon': dept_config.get('icon', '📁'),     # Use config icon or default
            'from_config': dept_id in dept_map         # Flag if from config
        })
    
    # 4. Also add departments from config that don't exist in folders yet
    # (for creating new departments)
    for dept_id, dept_config in dept_map.items():
        if dept_id not in scanned_dept_ids:
            departments.append({
                'id': dept_id,
                'name': dept_config.get('name', dept_id),
                'icon': dept_config.get('icon', '📁'),
                'from_config': True
            })
    
    return departments

def collect_files_with_filters(base_dir, type_name, department=None, subdept=None, username=None):
    """
    Main scan logic for files with filters (working .hip files only)
    Supports: dept/files, dept/subdept/files, dept/user/files, dept/subdept/user/files
    
    Args:
        base_dir: Project root directory
        type_name: Type name (e.g., "_characters", "Shots")
        department: Department filter (optional)
        subdept: Subdepartment filter (optional)
        username: User workspace filter (optional)
    Returns: List of (filepath, asset_name, department_name, file_info) tuples
    """
    if not base_dir or not type_name:
        return []
    
    results = []
    is_assets = type_name != "Shots"
    file_extensions = HOUDINI_EXTS  # Always scan .hip files only
    
    def scan_directory_recursive(scan_path, asset_name, dept_name, max_depth=2, current_depth=0, is_shots=False):
        """Recursively scan directory for files, skipping subdepts/users not in filter"""
        if current_depth > max_depth or not os.path.isdir(scan_path):
            return
        
        for entry in os.scandir(scan_path):
            if entry.name.startswith('.') or entry.name in IGNORE_FOLDERS:
                continue
            
            if entry.is_file():
                # Found a file - check if it's a valid Houdini file
                if os.path.splitext(entry.name)[1].lower() in file_extensions:
                    # For shots, extract shot name from filename instead of using dept name
                    display_name = asset_name
                    if is_shots:
                        display_name = infer_shot(entry.path)
                    
                    file_info = {
                        'filename': entry.name,
                        'version': parse_ver(entry.name),
                        'size': entry.stat().st_size,
                        'modified': entry.stat().st_mtime
                    }
                    results.append((entry.path, display_name, dept_name, file_info))
            
            elif entry.is_dir():
                # Found a subdirectory - could be subdept or user workspace
                # Continue scanning recursively
                scan_directory_recursive(entry.path, asset_name, dept_name, max_depth, current_depth + 1, is_shots)
    
    try:
        if is_assets:
            # Assets: scan type/asset_name/department/[subdept/][user/]files
            type_dir = os.path.join(base_dir, "01_assets", type_name)
            if not os.path.isdir(type_dir):
                return []
            
            for asset_entry in os.scandir(type_dir):
                if (asset_entry.is_dir() and 
                    not asset_entry.name.startswith('.') and 
                    asset_entry.name not in IGNORE_FOLDERS):
                    
                    asset_name = asset_entry.name
                    
                    # Scan departments within this asset
                    for dept_entry in os.scandir(asset_entry.path):
                        if (dept_entry.is_dir() and 
                            not dept_entry.name.startswith('.') and 
                            dept_entry.name not in IGNORE_FOLDERS):
                            
                            dept_name = dept_entry.name
                            
                            # Apply department filter
                            if department and dept_name != department:
                                continue
                            
                            # Determine scan path based on subdept filter
                            if subdept:
                                # Only scan specific subdepartment
                                scan_path = os.path.join(dept_entry.path, subdept)
                                if not os.path.isdir(scan_path):
                                    continue
                                
                                # Apply username filter if specified
                                if username:
                                    # Only scan specific user workspace in this subdept
                                    user_path = os.path.join(scan_path, username)
                                    if os.path.isdir(user_path):
                                        scan_directory_recursive(user_path, asset_name, dept_name, max_depth=1)
                                else:
                                    # Scan all (users and direct files) in this subdept
                                    scan_directory_recursive(scan_path, asset_name, dept_name, max_depth=2)
                            else:
                                # No subdept filter - scan entire department
                                if username:
                                    # When subdept=None and username specified, scan user workspace in ALL subdepts
                                    # First, try direct user workspace in department root
                                    user_path = os.path.join(dept_entry.path, username)
                                    if os.path.isdir(user_path):
                                        scan_directory_recursive(user_path, asset_name, dept_name, max_depth=1)
                                    
                                    # Then scan user workspace in each subdept
                                    for subdept_entry in os.scandir(dept_entry.path):
                                        if (subdept_entry.is_dir() and 
                                            not subdept_entry.name.startswith('.') and 
                                            subdept_entry.name not in IGNORE_FOLDERS):
                                            user_path = os.path.join(subdept_entry.path, username)
                                            if os.path.isdir(user_path):
                                                scan_directory_recursive(user_path, asset_name, dept_name, max_depth=1)
                                else:
                                    # Scan all (subdepts, users, and direct files) in department
                                    scan_directory_recursive(dept_entry.path, asset_name, dept_name, max_depth=2)
        else:
            # Shots: scan department/[subdept/][user/]files
            shots_dir = os.path.join(base_dir, "02_shots")
            if not os.path.isdir(shots_dir):
                return []
            
            for dept_entry in os.scandir(shots_dir):
                if (dept_entry.is_dir() and 
                    not dept_entry.name.startswith('.') and 
                    dept_entry.name not in IGNORE_FOLDERS):
                    
                    dept_name = dept_entry.name
                    
                    # Apply department filter
                    if department and dept_name != department:
                        continue
                    
                    # For shots, shot name will be extracted from filename in scan function
                    shot_name = ""  # Placeholder, will be extracted from filename
                    
                    # Determine scan path based on subdept filter
                    if subdept:
                        # Only scan specific subdepartment
                        scan_path = os.path.join(dept_entry.path, subdept)
                        if not os.path.isdir(scan_path):
                            continue
                        
                        # Apply username filter if specified
                        if username:
                            # Only scan specific user workspace in this subdept
                            user_path = os.path.join(scan_path, username)
                            if os.path.isdir(user_path):
                                scan_directory_recursive(user_path, shot_name, dept_name, max_depth=1, is_shots=True)
                        else:
                            # Scan all (users and direct files) in this subdept
                            scan_directory_recursive(scan_path, shot_name, dept_name, max_depth=2, is_shots=True)
                    else:
                        # No subdept filter - scan entire department
                        if username:
                            # When subdept=None and username specified, scan user workspace in ALL subdepts
                            # First, try direct user workspace in department root
                            user_path = os.path.join(dept_entry.path, username)
                            if os.path.isdir(user_path):
                                scan_directory_recursive(user_path, shot_name, dept_name, max_depth=1, is_shots=True)
                            
                            # Then scan user workspace in each subdept
                            for subdept_entry in os.scandir(dept_entry.path):
                                if (subdept_entry.is_dir() and 
                                    not subdept_entry.name.startswith('.') and 
                                    subdept_entry.name not in IGNORE_FOLDERS):
                                    user_path = os.path.join(subdept_entry.path, username)
                                    if os.path.isdir(user_path):
                                        scan_directory_recursive(user_path, shot_name, dept_name, max_depth=1, is_shots=True)
                        else:
                            # Scan all (subdepts, users, and direct files) in department
                            scan_directory_recursive(dept_entry.path, shot_name, dept_name, max_depth=2, is_shots=True)
                            
    except Exception as e:
        if DEBUG: print(f"⚠️ Error collecting files with filters: {e}")
    
    return results

def find_thumbnail(file_path, department_path):
    """
    Search for thumbnail in _thumbnail/ folder
    Args:
        file_path: Full path to the file
        department_path: Path to the department folder
    Returns: Path to thumbnail file or None
    """
    if not file_path or not department_path:
        return None
    
    try:
        # Get filename without extension
        filename = os.path.basename(file_path)
        name_no_ext = os.path.splitext(filename)[0]
        
        # Look for _thumbnail folder in department
        thumbnail_dir = os.path.join(department_path, "_thumbnail")
        if not os.path.isdir(thumbnail_dir):
            return None
        
        # Search for thumbnail with priority order
        extensions = ['.jpg', '.png', '.jpeg', '.bmp']
        
        # First try: exact match with version
        for ext in extensions:
            thumb_path = os.path.join(thumbnail_dir, f"{name_no_ext}{ext}")
            if os.path.isfile(thumb_path):
                return thumb_path
        
        # Second try: match without version
        name_no_version = re.sub(r'_v\d+$', '', name_no_ext)
        for ext in extensions:
            thumb_path = os.path.join(thumbnail_dir, f"{name_no_version}{ext}")
            if os.path.isfile(thumb_path):
                return thumb_path
        
        # Third try: match just the base name (before any separators)
        base_name = re.split(r'[_-]', name_no_version)[0]
        for ext in extensions:
            thumb_path = os.path.join(thumbnail_dir, f"{base_name}{ext}")
            if os.path.isfile(thumb_path):
                return thumb_path
                
    except Exception as e:
        if DEBUG: print(f"⚠️ Error finding thumbnail for {file_path}: {e}")
    
    return None

def get_supported_file_extensions():
    """
    Get supported file extensions for File Manager (working files only)
    Returns: Set of Houdini file extensions
    """
    return HOUDINI_EXTS

def get_all_file_extensions():
    """
    Get all supported file extensions for Asset Manager
    Returns: Set of all file extensions
    Note: This function is for future Asset Manager tool
    """
    return {
        '.hip', '.hiplc', '.hipnc',  # Houdini files
        '.fbx', '.usd', '.abc', '.obj', '.ma', '.mb',  # 3D files
        '.jpg', '.png', '.jpeg', '.bmp', '.tga', '.exr',  # Images
        '.mp4', '.mov', '.avi', '.mkv',  # Videos
        '.txt', '.json', '.xml', '.md'  # Text files
    }



