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
        ver_str = f"v{ver_match.group(1)}"
        new_ver_str = f"v{new_ver_num:03d}"
        new_ver_pattern = ver_pattern.replace(ver_str, new_ver_str)
        new_filename = name.replace(ver_pattern, new_ver_pattern)
        if note and note.strip():
            clean_note = re.sub(r'[^\w\s-]', '', note.strip())
            clean_note = re.sub(r'[\s]+', '_', clean_note)
            if clean_note: new_filename = f"{new_filename}_{clean_note}"
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
    """Get standard department list for asset creation"""
    return [
        "01_modeling",
        "02_rigging",
        "03_surfacing",
        "04_lookdev",
        "05_groom",
        "06_anim",
        "07_turntable",
    ]

def create_asset_folder_structure(base_dir, type_name, asset_name, departments=None):
    """
    Create complete folder structure for a new asset
    
    Args:
        base_dir: Project root directory
        type_name: Asset type like "_characters"
        asset_name: Asset name like "char_Cyborg" (with prefix) or "Cyborg" (auto-prefix)
        departments: List of department folders to create (None = use standard)
    
    Returns:
        (success, asset_folder_path, message)
    """
    try:
        # Add prefix if not present
        if not any(asset_name.lower().startswith(p) for p in ['char_', 'prop_', 'env_', 'veh_', 'fx_']):
            # Guess prefix from type
            if 'character' in type_name.lower():
                asset_name = f"char_{asset_name}"
            elif 'prop' in type_name.lower():
                asset_name = f"prop_{asset_name}"
            elif 'environment' in type_name.lower():
                asset_name = f"env_{asset_name}"
            elif 'vehicle' in type_name.lower():
                asset_name = f"veh_{asset_name}"
            elif 'fx' in type_name.lower() or 'effect' in type_name.lower():
                asset_name = f"fx_{asset_name}"
        
        # Create asset base folder
        asset_folder = os.path.join(base_dir, "01_assets", type_name, asset_name)
        
        if os.path.exists(asset_folder):
            return False, asset_folder, f"Asset folder already exists:\n{asset_folder}"
        
        # Use standard departments if not specified
        if not departments:
            departments = get_standard_departments()
        
        # Create all department folders
        created_folders = []
        for dept in departments:
            dept_path = os.path.join(asset_folder, dept)
            os.makedirs(dept_path, exist_ok=True)
            created_folders.append(dept)
        
        success_msg = f"Asset folder created successfully!\n\n"
        success_msg += f"Asset: {asset_name}\n"
        success_msg += f"Location: {asset_folder}\n\n"
        success_msg += f"Departments created:\n"
        for dept in created_folders:
            success_msg += f"  • {dept}\n"
        
        return True, asset_folder, success_msg
        
    except Exception as e:
        return False, "", f"Failed to create asset folder:\n{str(e)}"

def generate_new_filename(type_name, asset_name, department, version="v001", ext=".hip"):
    """
    Generate filename in format: $type_$assetname_$department_$version.ext
    
    Args:
        type_name: Type like "_characters" → "characters"
        asset_name: Asset like "char_Cyborg" → "Cyborg"
        department: Department like "01_modeling" → "modeling"
        version: Version string like "v001"
        ext: File extension like ".hip"
    
    Returns:
        Filename like "characters_Cyborg_modeling_v001.hip"
    """
    clean_type = clean_type_name(type_name)
    clean_asset = clean_asset_name(asset_name)
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

def collect_files_with_filters(base_dir, type_name, department=None):
    """
    Main scan logic for files with filters (working .hip files only)
    Args:
        base_dir: Project root directory
        type_name: Type name (e.g., "_characters", "Shots")
        department: Department filter (optional)
    Returns: List of (filepath, asset_name, department_name, file_info) tuples
    """
    if not base_dir or not type_name:
        return []
    
    results = []
    is_assets = type_name != "Shots"
    file_extensions = HOUDINI_EXTS  # Always scan .hip files only
    
    try:
        if is_assets:
            # Assets: scan type/asset_name/department/files
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
                            
                            # Scan working files only (not in _publish/)
                            scan_path = dept_entry.path
                            
                            if not os.path.isdir(scan_path):
                                continue
                            
                            # Scan files
                            for file_entry in os.scandir(scan_path):
                                if (file_entry.is_file() and 
                                    os.path.splitext(file_entry.name)[1].lower() in file_extensions):
                                    
                                    file_info = {
                                        'filename': file_entry.name,
                                        'version': parse_ver(file_entry.name),
                                        'size': file_entry.stat().st_size,
                                        'modified': file_entry.stat().st_mtime
                                    }
                                    
                                    results.append((file_entry.path, asset_name, dept_name, file_info))
        else:
            # Shots: scan department/files
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
                    
                    # Scan working files only (not in _publish/)
                    scan_path = dept_entry.path
                    
                    if not os.path.isdir(scan_path):
                        continue
                    
                    # Scan files
                    for file_entry in os.scandir(scan_path):
                        if (file_entry.is_file() and 
                            os.path.splitext(file_entry.name)[1].lower() in file_extensions):
                            
                            # Extract shot name from filename
                            shot_name = infer_shot(file_entry.path)
                            
                            file_info = {
                                'filename': file_entry.name,
                                'version': parse_ver(file_entry.name),
                                'size': file_entry.stat().st_size,
                                'modified': file_entry.stat().st_mtime
                            }
                            
                            results.append((file_entry.path, shot_name, dept_name, file_info))
                            
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



