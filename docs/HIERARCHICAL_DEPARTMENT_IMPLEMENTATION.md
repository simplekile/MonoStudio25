# Hierarchical Department Menu with Subdepartments & User Workspaces

## ✅ Implementation Complete

**Date**: 2024-12-19  
**Version**: 2.3.0  
**Status**: Ready for Testing

---

## 🎯 Overview

Implemented hierarchical department menu system with support for:
1. **Subdepartments** (config-based system folders)
2. **User workspaces** (personal work folders)
3. **User metadata tracking** (.mono/users.json)

---

## 📋 Features Implemented

### 1. Subdepartment Support

**Config-driven subdepartments:**
- Pattern: `\d{2}_[a-z][a-z0-9_]*` (e.g., `01_sculpt`, `02_retopo`, `03_uv`)
- Must be defined in `config/department_structure_v2.json`
- Shown in hierarchical menu under parent department

**Example structure:**
```
01_modeling/
  ├── 01_sculpt/       # Subdepartment (from config)
  ├── 02_retopo/       # Subdepartment (from config)
  ├── 03_uv/           # Subdepartment (from config)
  ├── john/            # User workspace
  └── mary/            # User workspace
```

### 2. User Workspace Support

**Auto-detected user workspaces:**
- Pattern: `^[a-z0-9_]+$` (lowercase alphanumeric + underscore)
- Cannot start with `\d{2}_` (reserved for subdepartments)
- Examples: `john`, `mary`, `techartist`, `david_work`

**User detection:**
- Auto-detect from OS: `getpass.getuser()`
- Custom override in Settings: `user_name` setting
- Validation: lowercase, max 20 chars, no numeric prefix

### 3. User Metadata Tracking

**Metadata file: `.mono/users.json`**
```json
{
  "users": {
    "john": {
      "full_name": "John Smith",
      "email": "john@studio.com",
      "department": "Modeling",
      "created": "2024-12-19T10:30:00",
      "last_active": "2024-12-19T15:45:00"
    }
  },
  "version": "1.0"
}
```

**Auto-registration:**
- User activity tracked automatically
- First file save creates user entry
- Last activity updated on each operation

### 4. Hierarchical Menu UI

**Department menu behavior:**
- Departments **with** subdepartments → Show submenu
- Departments **without** subdepartments → Direct action

**Submenu structure:**
```
📁 01_modeling
  ├─ 📁 All files (25)       # All dept files
  ├─ ───────────
  ├─   └─ Sculpt (10)        # Subdept only
  ├─   └─ Retopo (8)         # Subdept only
  └─   └─ UV (7)             # Subdept only
```

**File counts:**
- Show total files for "All files" option
- Show specific counts for each subdepartment
- Includes files from user workspaces

---

## 🔧 Technical Changes

### File: `python/mono_tools/file_manager/file_manager_helpers.py`

**Added Constants:**
```python
SUBDEPT_PATTERN = re.compile(r'^\d{2}_[a-z][a-z0-9_]*$')
RESERVED_SYSTEM_FOLDERS = {'_publish', '_archive', '_thumbnail', 'Vers', 'backup'}
USER_WORKSPACE_PATTERN = re.compile(r'^[a-z0-9_]+$')
```

**Added Functions:**
- `get_subdepartments_for_department(dept_id)` - Get subdepts from config
- `is_subdepartment_folder(folder_name, dept_id)` - Check if folder is subdept
- `is_user_workspace(folder_name)` - Check if folder is user workspace
- `validate_username(username)` - Validate username format
- `get_current_username()` - Get current user (auto-detect or custom)
- `load_user_metadata(project_root)` - Load user metadata
- `save_user_metadata(project_root, metadata)` - Save user metadata
- `register_user_activity(...)` - Register/update user activity

**Updated Functions:**
- `collect_files_with_filters(base_dir, type_name, department, subdept=None, username=None)`
  - Added `subdept` and `username` parameters
  - Recursive scanning with max_depth=2
  - Supports: dept/files, dept/subdept/files, dept/user/files, dept/subdept/user/files

### File: `python/mono_tools/file_manager/file_manager_minibar.py`

**Added Instance Variables:**
```python
self.current_subdept = None  # Track subdepartment selection
```

**Updated Methods:**

**`__init__()` (line ~80):**
- Added `self.current_subdept = None`

**`_show_dept_menu()` (line ~325-434):**
- Complete rewrite for hierarchical menu
- Load subdepartments from config
- Create submenus for depts with subdepts
- Show file counts for each option
- Bold current selection

**`_select_department(dept_name, subdept_name=None)` (line ~459-491):**
- Added `subdept_name` parameter
- Update button text for dept/subdept display
- Save both dept and subdept to QSettings
- Truncate text to fit button (10 chars max)

**`_refresh_files_standalone()` (line ~1688-1748):**
- Pass `subdept=subdepartment` to `collect_files_with_filters()`
- Include subdept in debug output

**`_load_minibar_settings()` (line ~1754-1791):**
- Load saved subdepartment from settings
- Pass subdept to `_select_department()` on restore

---

## 📁 Folder Structure Examples

### Assets with Subdepartments & Users:
```
01_assets/
  _characters/
    char_Cyborg/
      01_modeling/
        01_sculpt/                          # Subdept (config)
          john/                             # User workspace
            char_Cyborg_sculpt_v001.hip
          mary/
            char_Cyborg_sculpt_v001.hip
          _publish/                         # Published files
        02_retopo/                          # Subdept (config)
          john/
            char_Cyborg_retopo_v001.hip
        char_Cyborg_modeling_v001.hip       # Direct dept file
        john/                               # User workspace at dept level
          char_Cyborg_modeling_wip_v001.hip
```

### Shots with Subdepartments:
```
02_shots/
  sq010_sh0010/
    01_animation/
      john/
        sq010_sh0010_anim_v001.hip
      mary/
        sq010_sh0010_anim_v002.hip
```

---

## 🎨 Naming Convention Rules

### 1. Subdepartments (System)
- **Pattern**: `^\d{2}_[a-z][a-z0-9_]*$`
- **Examples**: `01_sculpt`, `02_retopo`, `03_uv`, `01_texture`
- **Requirements**:
  - Start with 2 digits (01-99) + underscore
  - Lowercase letters, numbers, underscore only
  - Must be defined in `department_structure_v2.json`

### 2. User Workspaces (Personal)
- **Pattern**: `^[a-z0-9_]+$` (NO `\d{2}_` prefix)
- **Examples**: `john`, `mary`, `david_nguyen`, `techartist`
- **Requirements**:
  - Lowercase letters, numbers, underscore only
  - Cannot start with `\d{2}_` pattern
  - Max 20 characters
  - Auto-detected from OS or custom in settings

### 3. Reserved System Folders
- `_publish/` - Published files
- `_archive/` - Archived content
- `_thumbnail/` - Thumbnails
- `Vers/` - Version backups
- `backup/` - Backups

---

## 🧪 Testing Scenarios

### Scenario 1: Department with Subdepartments
1. Open MiniBar
2. Select Type: `_characters`
3. Click Dept button
4. See: `01_modeling` with submenu arrow
5. Hover over `01_modeling`
6. See submenu with: All files, Sculpt, Retopo, UV
7. Select `Sculpt`
8. Button shows: `📁 mod/sculpt`
9. Files filtered to sculpt subdept only

### Scenario 2: Department without Subdepartments
1. Select Type: `_characters`
2. Click Dept button
3. See: `02_rigging` as direct action
4. Click `02_rigging`
5. Button shows: `📁 rigging`
6. Files show all rigging files

### Scenario 3: Mixed Files (Dept + Subdept + User)
Structure:
```
01_modeling/
  file_at_dept_level.hip
  01_sculpt/
    john/
      sculpt_v001.hip
  john/
    wip_v001.hip
```

Expected behavior:
- Select "All files" → Shows all 3 files
- Select "Sculpt" → Shows only `sculpt_v001.hip`

### Scenario 4: User Metadata Tracking
1. User `john` saves first file
2. Check `.mono/users.json` created
3. Contains john's entry with timestamp
4. User saves another file
5. `last_active` timestamp updated

### Scenario 5: Settings Persistence
1. Select `_characters` / `01_modeling` / `01_sculpt`
2. Close Houdini
3. Reopen Houdini
4. MiniBar restores exact selection
5. Button shows: `📁 mod/sculpt`

---

## 🚀 Usage Guide

### For Artists:

**1. Basic Workflow:**
```
1. Open Houdini
2. MiniBar appears (top-right)
3. Select Type (🏷️): _characters
4. Select Dept (📁): 01_modeling → Sculpt
5. Files filtered to sculpt subdept
6. Save file → Auto-creates user workspace
```

**2. Your Files Location:**
```
01_assets/_characters/char_Cyborg/01_modeling/01_sculpt/yourname/
```

**3. User Settings:**
```
Click ⚙️ Settings
→ Change username if needed
→ Enter full name, email (optional)
```

### For TDs:

**1. Add Subdepartments:**
Edit `config/department_structure_v2.json`:
```json
{
  "id": "01_modeling",
  "subdepartments": [
    {"id": "01_sculpt", "name": "Sculpt", "create_publish": true},
    {"id": "02_retopo", "name": "Retopo", "create_publish": true},
    {"id": "03_uv", "name": "UV", "create_publish": false}
  ]
}
```

**2. User Metadata Management:**
```python
from mono_tools.file_manager.file_manager_helpers import load_user_metadata

# Load metadata
metadata = load_user_metadata("/path/to/project")

# Check users
for username, info in metadata['users'].items():
    print(f"{username}: {info['full_name']} - {info['last_active']}")
```

---

## 📊 Benefits

### 1. Better Organization
- Clear separation: subdepts vs user workspaces
- Hierarchical navigation
- Visual distinction in UI

### 2. Ownership Tracking
- Know who worked on which file
- Metadata persists with project
- No centralized database needed

### 3. Flexible Structure
- Config-driven subdepartments
- Auto-detected user workspaces
- No manual registration required

### 4. Industry Standard
- Follows ftrack/Shotgun patterns
- Config-based structure definition
- User-friendly naming convention

---

## 🔮 Future Enhancements

### Phase 2 (Optional):
1. **User Filter Button**
   - Filter files by specific user
   - Show "My Files" vs "All Files"

2. **User Profile Dialog**
   - Edit full name, email, department
   - View activity history
   - Avatar support

3. **Publish Workflow**
   - Publish from user workspace to `_publish/`
   - Version tracking
   - Approval workflow

4. **Team Dashboard**
   - See who's working on what
   - File locking (optional)
   - Activity feed

---

## 📝 Migration Notes

### For Existing Projects:

**1. No Breaking Changes:**
- Old structure still works
- Flat departments supported
- No forced migration

**2. Gradual Adoption:**
- Add subdepartments to config as needed
- Artists create user workspaces naturally
- Metadata builds over time

**3. Backward Compatible:**
- `collect_files_with_filters()` parameters optional
- `_select_department(dept)` still works
- Settings restore gracefully

---

## 🐛 Known Limitations

1. **Shot Structure:** Subdepartments work for assets, shots need testing
2. **Software Folders:** Not yet integrated with menu (Houdini, Maya, etc.)
3. **User Validation:** No duplicate username checking across projects
4. **Metadata Sync:** No cloud sync for `.mono/users.json`

---

## 📚 Related Files

- `config/department_structure_v2.json` - Department & subdepartment definitions
- `.mono/users.json` - User metadata (per project)
- `python/mono_tools/file_manager/file_manager_helpers.py` - Core logic
- `python/mono_tools/file_manager/file_manager_minibar.py` - UI implementation

---

## ✅ Checklist

- [x] Subdepartment helper functions
- [x] User workspace detection
- [x] User metadata system
- [x] Hierarchical menu UI
- [x] File scanning with subdepts
- [x] Settings persistence
- [x] Naming convention validation
- [x] Documentation

---

## 🎉 Ready for Testing!

**Next Steps:**
1. Test with real project structure
2. Verify hierarchical menu display
3. Test file scanning accuracy
4. Check user metadata creation
5. Verify settings persistence

**Test Project Structure:**
```
project_root/
  .mono/
    users.json
  01_assets/
    _characters/
      char_Hero/
        01_modeling/
          01_sculpt/
          02_retopo/
          john/
        02_rigging/
          john/
```

---

**Implementation Complete** ✨

