# New Folder Dialog - Complete Implementation

## ✅ Complete

**Feature**: Custom New Folder Dialog with radio buttons for Asset/Shot  
**Version**: 2.3.0  
**Status**: Ready for Testing

---

## 🎯 New Folder Dialog Design

### Single Dialog with Radio Buttons:

```
┌────────────────────────────────────────────────────┐
│ Create New Folder                              ×  │
├────────────────────────────────────────────────────┤
│                                                    │
│ ┌─ Folder Type ─────────────────────────────────┐ │
│ │  ● Asset Folder    ○ Shot Folder              │ │
│ └───────────────────────────────────────────────┘ │
│                                                    │
│ [Asset Form - visible when Asset selected]        │
│                                                    │
│    Asset Type: [🧑 Characters                 ▼] │
│    Asset Name: [Hero                           ] │
│                                                    │
│ Folder Structure Preview:                         │
│ ┌──────────────────────────────────────────────┐ │
│ │ 01_assets/_characters/char_Hero/             │ │
│ │   ├─ 🎨 01_modeling/ (Modeling)              │ │
│ │   │  ├─ 01_sculpt/ (Sculpt)                  │ │
│ │   │  │  └─ _publish/                         │ │
│ │   │  ├─ 02_retopo/ (Retopo)                  │ │
│ │   │  │  └─ _publish/                         │ │
│ │   │  ├─ 03_uv/ (UV)                          │ │
│ │   │  └─ _publish/                            │ │
│ │   ├─ 🦴 02_rigging/ (Rigging)                │ │
│ │   │  └─ _publish/                            │ │
│ │   ├─ 🎭 03_surfacing/ (Surfacing)            │ │
│ │   │  ├─ 01_texture/ (Texture)                │ │
│ │   │  └─ _publish/                            │ │
│ │   └─ ...                                     │ │
│ │                                              │ │
│ │ Total: 7 departments, 25 folders             │ │
│ └──────────────────────────────────────────────┘ │
│                                                    │
│                    [Cancel]  [Create Folder]      │
└────────────────────────────────────────────────────┘
```

---

## 📋 Features

### 1. Radio Button Toggle

**Asset Folder (●):**
- Shows: Asset Type dropdown, Asset Name input
- Preview: Asset structure with all departments + subdepartments
- Creates: `01_assets/{type}/{asset}/...`

**Shot Folder (○):**
- Shows: Shot Name input only
- Preview: Shot structure with all departments + subdepartments
- Creates: `02_shots/{shot}/...`

**Toggle behavior:**
- Click Asset → Show asset form, hide shot form
- Click Shot → Show shot form, hide asset form
- Preview updates automatically

---

### 2. Asset Type Dropdown

**Shows types from project scan:**
```
🧑 Characters       ← From scan (if exists in project)
🏞️ Environments     ← From scan
🎨 Graphic          ← From scan
```

**NOT from config** (only actual types in project)

---

### 3. Real-time Preview

**Updates when:**
- Radio button changed (Asset ↔ Shot)
- Asset type changed
- Asset/Shot name changed

**Preview shows:**
- Full folder tree structure
- Department icons and names
- Subdepartments with indentation
- Publish folders
- Accurate folder count

**Asset Preview Example:**
```
01_assets/_characters/char_Hero/
  ├─ 🎨 01_modeling/ (Modeling)
  │  ├─ 01_sculpt/ (Sculpt)     ← Subdepartment!
  │  │  └─ _publish/
  │  ├─ 02_retopo/ (Retopo)
  │  │  └─ _publish/
  │  ├─ 03_uv/ (UV)
  │  └─ _publish/
  ├─ 🦴 02_rigging/ (Rigging)
  │  └─ _publish/
  └─ ...

Total: 7 departments, 25 folders
```

**Shot Preview Example:**
```
02_shots/sq010_sh0010/
  ├─ 🎬 01_animation/ (Animation)
  ├─ 💨 02_sim/ (Simulation)
  │  ├─ 01_crowd/ (Crowd)       ← Subdepartment!
  │  │  └─ _publish/
  │  ├─ 02_cloth/ (Cloth)
  │  │  └─ _publish/
  │  ├─ 03_destruction/ (Destruction)
  │  │  └─ _publish/
  │  └─ _publish/
  └─ ...

Total: 4 departments, 14 folders
```

---

### 4. Validation

**Asset Folder:**
- ✅ Asset type must be selected
- ✅ Asset name must be entered

**Shot Folder:**
- ✅ Shot name must be entered
- ⚠️ Warning if name doesn't match `sq###_sh####` format (but allows continue)

---

## 🔧 Technical Implementation

### File: `python/mono_tools/file_manager/ui/new_folder_dialog.py`

**Class: `NewFolderDialog`**

**Constructor:**
```python
NewFolderDialog(
    parent=None,
    all_types=None,      # Scanned types from project
    asset_types=None     # Config for icons/names
)
```

**Key Methods:**

**`_setup_ui()`** - Build dialog
- Title
- Radio buttons (Asset/Shot)
- Asset form (type dropdown, name input)
- Shot form (name input)
- Preview text (QTextEdit)
- Folder count label
- Buttons (Cancel/Create)

**`_update_form_visibility()`** - Toggle forms
- Asset radio checked → Show asset form, hide shot form
- Shot radio checked → Show shot form, hide asset form

**`_update_asset_preview()`** - Preview for assets
- Load departments from config
- Build tree structure string
- Show subdepartments
- Count folders

**`_update_shot_preview()`** - Preview for shots
- Load shot departments from config
- Build tree structure string
- Show subdepartments  
- Count folders

**`_on_create()`** - Validate
- Check type/name based on radio selection
- Validate shot name format (optional)
- Accept if valid

**`get_values()`** - Return data
```python
{
    'is_asset': True/False,
    'asset_type': '...' or None,
    'asset_name': '...' or None,
    'shot_name': '...' or None
}
```

---

### File: `python/mono_tools/file_manager/file_manager_minibar.py`

**Updated `_new_folder()` (line ~1178-1234)**

**Before:**
```python
# Show ChoiceDialog → Asset or Shot
# If Asset: _new_asset_folder()
# If Shot: _new_shot_folder()
```

**After:**
```python
# Scan project types
# Show NewFolderDialog (single dialog)
# Get values
# If asset: _create_asset_folder_from_dialog()
# If shot: _create_shot_folder_from_dialog()
```

---

**Renamed Methods:**

**`_create_asset_folder_from_dialog()` (was `_new_asset_folder`)**
- Simplified: No UI logic
- Just folder creation from dialog values

**`_create_shot_folder_from_dialog()` (was `_new_shot_folder`)**
- Simplified: No UI logic  
- Just folder creation from dialog values
- Added subdepartment creation logic

---

## 🎯 Complete Flow

### Asset Folder Creation:

```
1. Click ⚡ → New Folder
   ↓
2. Dialog opens:
   ● Asset Folder  ○ Shot Folder  ← Default: Asset
   ↓
3. Asset form visible:
   Asset Type: [🧑 Characters ▼]  ← Select
   Asset Name: [Hero           ]  ← Enter
   ↓
4. Preview updates live:
   01_assets/_characters/char_Hero/
     ├─ 01_modeling/
     │  ├─ 01_sculpt/       ← Shows subdepartments!
     │  ├─ 02_retopo/
     │  └─ 03_uv/
     ...
   
   Total: 7 departments, 25 folders
   ↓
5. Click "Create Folder"
   ↓
6. All folders created with subdepartments
   ↓
7. Success message → Option to create file
```

---

### Shot Folder Creation:

```
1. Click ⚡ → New Folder
   ↓
2. Dialog opens → Click: ○ Shot Folder
   ↓
3. Asset form hides, Shot form shows:
   Shot Name: [sq010_sh0010  ]  ← Enter
   ↓
4. Preview updates:
   02_shots/sq010_sh0010/
     ├─ 01_animation/
     ├─ 02_sim/
     │  ├─ 01_crowd/        ← Shows subdepartments!
     │  ├─ 02_cloth/
     │  └─ 03_destruction/
     ...
   
   Total: 4 departments, 14 folders
   ↓
5. Click "Create Folder"
   ↓
6. All folders created with subdepartments
   ↓
7. Success message → Option to create file
```

---

## 🎨 UI Features

### Radio Buttons:
- Large, clear toggle
- Icons: 🎨 Asset, 🎬 Shot
- Instant form switching
- Consistent with dialog theme

### Preview Text:
- Monospace font (Consolas)
- Dark background `#1a1a1a`
- Light gray text `#aaa`
- Scrollable if long
- Real-time updates
- Shows subdepartments properly

### Styling:
- Matches MiniBar theme
- Matches New File Dialog
- Consistent colors/fonts
- Professional appearance

---

## ✅ Benefits

### 1. Single Dialog
- No ChoiceDialog → InputDialog flow
- Everything in one place
- Easier to use

### 2. Full Preview
- See exactly what will be created
- Shows subdepartments
- Accurate folder count
- No surprises

### 3. Flexible
- Can switch Asset ↔ Shot
- Can change asset type
- Real-time feedback

### 4. Consistent
- Same UI as New File Dialog
- Same styling as MiniBar
- Professional appearance

---

## 🧪 Testing Guide

### Test 1: Asset Folder Creation
```
1. Click ⚡ → New Folder
2. Ensure "Asset Folder" selected
3. Select Type: Characters
4. Enter Name: "Hero"
5. Check preview shows:
   - 01_modeling with subdepts ✅
   - 03_surfacing with subdepts ✅
6. Click Create
7. Verify all folders created
8. Verify subdepartments created
```

### Test 2: Shot Folder Creation
```
1. Click ⚡ → New Folder
2. Click "Shot Folder" radio
3. Asset form hides ✅
4. Shot form shows ✅
5. Enter Name: "sq010_sh0010"
6. Check preview shows:
   - 02_sim with subdepts ✅
7. Click Create
8. Verify all folders created
9. Verify subdepartments created
```

### Test 3: Toggle Radio Buttons
```
1. Select Asset Folder
2. Fill asset fields
3. See asset preview
4. Click Shot Folder radio
5. Asset form hides ✅
6. Shot form shows ✅
7. Preview changes to shot structure ✅
8. Toggle back to Asset
9. Previous values preserved ✅
```

### Test 4: Type Dropdown
```
1. Asset Folder selected
2. Type dropdown shows only existing types:
   - _characters (if exists)
   - _graphic (if exists)
   - NOT _props (if doesn't exist)
3. Can select any existing type ✅
```

---

## 📊 Complete Implementation

**Files Created:**
- `python/mono_tools/file_manager/ui/new_folder_dialog.py` - Custom dialog

**Files Modified:**
- `python/mono_tools/file_manager/ui/__init__.py` - Export NewFolderDialog
- `python/mono_tools/file_manager/file_manager_minibar.py` - Use new dialog

**Methods Updated:**
- `_new_folder()` - Use NewFolderDialog
- `_new_asset_folder()` → `_create_asset_folder_from_dialog()` - Simplified
- `_new_shot_folder()` → `_create_shot_folder_from_dialog()` - Simplified + subdepts

---

## ✨ Feature Summary

**New File Dialog:**
- ✅ All types dropdown (from project scan)
- ✅ All departments dropdown (updates per type)
- ✅ Subdepartments dropdown (updates per dept)
- ✅ User workspace input (auto-filled)
- ✅ Name input
- ✅ Real-time path preview

**New Folder Dialog:**
- ✅ Radio buttons (Asset/Shot)
- ✅ Type dropdown (assets from project)
- ✅ Name input (asset or shot)
- ✅ Real-time structure preview
- ✅ Subdepartments shown in preview
- ✅ Accurate folder count

**Both Dialogs:**
- ✅ Auto-filled from MiniBar
- ✅ Consistent UI styling
- ✅ Full validation
- ✅ User-friendly
- ✅ Professional appearance

---

## 🚀 Ready for Testing!

```python
# In Houdini (after restart):

from mono_tools import show_mono_minibar
show_mono_minibar()

# Test New File:
# 1. Make selections in MiniBar
# 2. Click ⚡ → New File
# 3. Custom dialog opens ✅
# 4. All fields auto-filled ✅
# 5. Can change type/dept/subdept ✅
# 6. Preview updates ✅

# Test New Folder:
# 1. Click ⚡ → New Folder
# 2. Custom dialog opens ✅
# 3. Radio buttons for Asset/Shot ✅
# 4. Preview shows subdepartments ✅
# 5. Create folder ✅
# 6. All subdepartments created ✅
```

---

**MonoStudio v2.3.0 - Complete!** 🎉

**All dialogs upgraded:**
- ✅ User Settings Dialog
- ✅ New File Dialog
- ✅ New Folder Dialog
- ✅ Consistent UI throughout

**© 2024 MonoStudio**

