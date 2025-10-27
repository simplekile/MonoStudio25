# New File Type Selection - Fixed

## ✅ Fixed

**Issue**: Type dropdown chỉ hiện type đang chọn  
**Solution**: Scan và hiện tất cả types có trong project structure  
**Version**: 2.3.0

---

## 🐛 Problem

### Before (Bug):
```
MiniBar selection: Shots
  ↓
New File Dialog opens:
  Type dropdown:
    🎬 Shots         ← Only this, can't change!
```

**Why?**
- Dialog chỉ load type hiện tại từ MiniBar
- Không load types khác
- User không thể tạo file cho type khác

---

## ✅ Solution

### After (Fixed):
```
MiniBar selection: Shots  
  ↓
New File Dialog opens:
  Type dropdown:
    🧑 Characters    ← Can select!
    🏞️ Environments  ← Can select!
    🎨 Graphic       ← Can select!
    🎬 Shots         ← Currently selected (auto-filled)
```

**Why it works now:**
- Scan project structure for ALL existing types
- Show all types in dropdown
- Auto-fill current type, but allow change
- Update departments when type changes

---

## 🔧 Technical Fix

### File: `python/mono_tools/file_manager/file_manager_minibar.py`

**Updated `_new_file()` (line ~997-1025):**

**Before:**
```python
# Only load current asset types from config
asset_types = load_asset_types_config() if is_assets else None

# Problem: Doesn't scan project, only loads config
```

**After:**
```python
# Scan actual types in project structure
from .file_manager_helpers import scan_project_types

scanned_types = scan_project_types(project_path)
# Returns: [(type_name, type_path, is_assets), ...]

# Convert to format for dialog
all_types_data = []
for type_name, type_path, is_assets in scanned_types:
    all_types_data.append((type_name, is_assets))

# Pass to dialog
dialog = NewFileDialog(..., all_types=all_types_data)
```

---

### File: `python/mono_tools/file_manager/ui/new_file_dialog.py`

**Updated Constructor (line ~13-24):**
```python
def __init__(self, ..., all_types=None):
    self.all_types = all_types or []  # All scanned types
```

**Updated `_populate_fields()` (line ~207-251):**

**Logic:**
```python
if self.all_types:
    # Use scanned types from project
    for type_name, is_assets in self.all_types:
        # Get icon from config
        icon = get_icon_for_type(type_name, is_assets)
        
        # Add to dropdown
        self.type_combo.addItem(f"{icon} {type_name}", (type_name, is_assets))
else:
    # Fallback to config-based types
    ...
```

---

## 📊 Type Sources

### Scanned from Project (NEW):
```python
scan_project_types(project_path)
  ↓
Scans:
  01_assets/
    _characters/  ← Found! (asset type)
    _environments/ ← Found! (asset type)
    _graphic/     ← Found! (asset type)
  02_shots/       ← Found! (shot type)
  ↓
Returns:
  [
    ("_characters", "path/to/_characters", True),
    ("_environments", "path/to/_environments", True),
    ("_graphic", "path/to/_graphic", True),
    ("Shots", "path/to/02_shots", False)
  ]
```

**Benefits:**
- ✅ Only shows types that exist in project
- ✅ Includes Shots if 02_shots/ folder exists
- ✅ Dynamic based on actual structure
- ✅ No config-only types (that don't exist yet)

---

## 🎯 Complete Flow

### User Workflow:

```
1. MiniBar:
   Type: Shots
   Dept: 03_lighting
   
2. Click ⚡ → New File
   ↓
3. Dialog opens:
   Type: [Dropdown showing ALL types from project]
         - 🧑 Characters      ← Can select
         - 🏞️ Environments    ← Can select  
         - 🎨 Graphic         ← Can select
         - 🎬 Shots           ← Auto-filled ✅
   
4. User changes type to "Characters"
   ↓
5. Department dropdown auto-updates:
   Old: Shot departments (01_animation, 02_sim, 03_lighting, 04_comp)
   New: Asset departments (01_modeling, 02_rigging, 03_surfacing, ...)
   ↓
6. User selects dept: "01_modeling"
   ↓
7. Subdepartment dropdown loads:
   (None), 01_sculpt, 02_retopo, 03_uv
   ↓
8. Select subdept: "01_sculpt"
   ↓
9. Preview updates:
   01_assets/_characters/char_Hero/01_modeling/01_sculpt/john/...
   ↓
10. Enter name: "Hero"
   ↓
11. Create file! ✅
```

---

## 📋 Type Dropdown Behavior

### Shows:
- ✅ All types that exist in project structure
- ✅ Both asset types and Shots (if they exist)
- ✅ Icons from config (if available)
- ✅ Display names from config (if available)

### Doesn't Show:
- ❌ Types from config that don't exist in project
- ❌ Types that haven't been created yet

### Example:

**Project structure:**
```
project/
  01_assets/
    _characters/   ← Exists
    _graphic/      ← Exists
  02_shots/        ← Exists
```

**Type dropdown shows:**
```
🧑 Characters     ← From scan
🎨 Graphic        ← From scan
🎬 Shots          ← From scan
```

**If config has `_props` and `_environments` but folders don't exist:**
```
Type dropdown WON'T show:
  _props          ← Not in project structure
  _environments   ← Not in project structure
```

---

## 🎨 Dynamic Updates

### Type Change → Department Updates:

```python
User selects Type: Characters (asset)
  ↓
_on_type_changed() triggers
  ↓
Load departments from config:
  if is_assets:
      departments = config['standard_departments']
  ↓
Department dropdown updates:
  🎨 01_modeling - Modeling
  🦴 02_rigging - Rigging
  🎭 03_surfacing - Surfacing
  ...
```

```python
User selects Type: Shots
  ↓
_on_type_changed() triggers
  ↓
Load departments from config:
  if not is_assets:
      departments = config['shot_departments']
  ↓
Department dropdown updates:
  🎬 01_animation - Animation
  💨 02_sim - Simulation
  💡 03_lighting - Lighting
  🎞️ 04_comp - Compositing
```

---

## 🧪 Test Cases

### Test 1: All Types Shown
```
1. Open New File Dialog
2. Click Type dropdown
3. Should see ALL types from project:
   - _characters (if exists)
   - _environments (if exists)
   - _graphic (if exists)
   - Shots (if 02_shots/ exists)
4. All selectable ✅
```

### Test 2: Switch Type
```
1. Type: Shots (auto-filled)
2. Dept: 03_lighting (auto-filled)
3. Change Type to: Characters
4. Dept dropdown updates to asset depts ✅
5. Select Dept: 01_modeling
6. Subdept dropdown shows: sculpt, retopo, uv ✅
7. Preview updates correctly ✅
```

### Test 3: Type Not in Project
```
Project has only:
  - _characters
  - Shots

Config has:
  - _characters
  - _props         ← Not in project
  - _environments  ← Not in project
  - Shots

Dialog shows:
  - _characters ✅
  - Shots ✅
  (No _props, _environments)
```

---

## ✅ Benefits

### 1. Accurate Type List
- Shows only what exists
- No confusion with config-only types
- Reflects actual project state

### 2. Flexible Workflow
- Can create file for any existing type
- Not locked to MiniBar selection
- Change type/dept/subdept freely

### 3. Smart Defaults
- Auto-fills from MiniBar
- But allows override
- Best of both worlds

### 4. Dynamic Updates
- Type → Departments update
- Dept → Subdepartments update
- Any field → Preview updates

---

## 📊 Complete Fix Summary

**Files Modified:**
1. `python/mono_tools/file_manager/file_manager_minibar.py`
   - Use `scan_project_types()` instead of `load_asset_types_config()`
   - Pass `all_types_data` to dialog

2. `python/mono_tools/file_manager/ui/new_file_dialog.py`
   - Add `all_types` parameter
   - Use `all_types` to populate dropdown
   - Show only types from project scan

**Result:**
- ✅ Type dropdown shows ALL types from project
- ✅ User can select any type
- ✅ Departments update when type changes
- ✅ Preview updates correctly
- ✅ Works for both assets and shots

---

## 🚀 Test Now

```python
# In Houdini:

# Restart to load changes
# Then:

from mono_tools import show_mono_minibar
show_mono_minibar()

# Test:
# 1. Any type/dept selection in MiniBar
# 2. Click ⚡ → New File
# 3. Click Type dropdown
# 4. Should see ALL types from project! ✅
# 5. Change type
# 6. Department updates ✅
# 7. Can create file for different type! ✅
```

---

**Fixed!** ✨

**MonoStudio v2.3.0** - Complete!

**© 2024 MonoStudio**

