import os, re, platform, subprocess, shutil, json
from datetime import datetime
from mono_tools.qt import QtCore, QtGui, QtWidgets
import hou

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
        print(f"⚠️ Error getting render folder path: {e}"); return None

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
        print(f"⚠️ list_projects error: {e}")
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
        print(f"⚠️ load_tabs_settings error: {e}")
    return [{"name": "lighting", "subpath": SUBPATH, "depth": 1}]

def save_tabs_settings(settings: 'QtCore.QSettings', tabs_conf):
    try:
        settings.setValue("tabs_v2", json.dumps(tabs_conf))
        settings.sync()
    except Exception as e:
        print(f"⚠️ save_tabs_settings error: {e}")



