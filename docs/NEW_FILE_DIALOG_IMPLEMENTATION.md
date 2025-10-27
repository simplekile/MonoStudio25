# New File Dialog - Custom UI Implementation

## ✅ Complete

**Feature**: Custom New File Dialog with auto-filled fields  
**Version**: 2.3.0  
**Status**: Ready for Testing

---

## 🎯 New File Dialog Design

### Dialog Layout:

```
┌─────────────────────────────────────────────────────────┐
│  Create New File                                    ×  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│          Type:  [🎬 Shots                          ▼]  │
│                                                         │
│    Department:  [💨 02_sim - Simulation            ▼]  │
│                                                         │
│ Subdepartment:  [01_crowd - Crowd                  ▼]  │
│                                                         │
│ User Workspace:  [john                              ]  │
│                  (lowercase, auto-detected)            │
│                                                         │
│     Shot Name:  [Sh010                              ]  │
│                                                         │
│ ─────────────────────────────────────────────────────  │
│                                                         │
│ File will be created at:                               │
│ ┌───────────────────────────────────────────────────┐ │
│ │ 02_shots/02_sim/01_crowd/john/Shots_Sh010_sim_... │ │
│ └───────────────────────────────────────────────────┘ │
│                                                         │
│                              [Cancel]  [Create File]   │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Features

### 1. Auto-filled Fields

**All fields populated from MiniBar:**
- ✅ Type → From MiniBar type selection
- ✅ Department → From MiniBar dept selection
- ✅ Subdepartment → From MiniBar subdept selection
- ✅ User Workspace → Auto-detected from system
- ❌ Name → User must enter (only field not auto-filled)

**User can change:**
- Type (dropdown with all available types)
- Department (dropdown with all departments)
- Subdepartment (dropdown with subdepts for selected dept)
- User Workspace (can override auto-detected)
- Name (required input)

---

### 2. Dynamic Subdepartment Dropdown

**Behavior:**
```
When Department changes:
  ↓
Load subdepartments for that department
  ↓
Update Subdepartment dropdown:
  - (None - Department root)    ← Default
  - 01_crowd - Crowd            ← From config
  - 02_cloth - Cloth
  - 03_destruction - Destruction
```

**If department has no subdepartments:**
```
Subdepartment dropdown shows only:
  - (None - Department root)
```

---

### 3. Real-time Path Preview

**Updates when any field changes:**
- Type changed → Preview updates
- Department changed → Preview updates
- Subdepartment changed → Preview updates
- User changed → Preview updates
- Name changed → Preview updates

**Preview examples:**
```
# With subdepartment:
02_shots/02_sim/01_crowd/john/Shots_Sh010_sim_v001.hip

# Without subdepartment:
02_shots/03_lighting/john/Shots_Sh010_lighting_v001.hip

# Assets:
01_assets/_characters/char_Hero/01_modeling/01_sculpt/john/characters_Hero_modeling_v001.hip
```

---

### 4. Validation

**On Create button click:**

**1. Type validation:**
```
if not type:
    → Error: "Please select a type"
```

**2. Department validation:**
```
if not department:
    → Error: "Please select a department"
```

**3. Username validation:**
```
if not username:
    → Error: "Please enter username"

if invalid pattern:
    → Error: "Invalid username: must be lowercase..."
```

**4. Name validation:**
```
if not name:
    → Error: "Please enter asset/shot name"
```

**All valid → Create file!**

---

## 🎨 UI Consistency

### Styling matches MiniBar:

**Colors:**
- Background: `#2b2b2b` (dialog)
- Input bg: `#1e1e1e` (dark)
- Border: `#3a3a3a` (subtle)
- Focus: `#3d5a99` (blue highlight)
- Text: `#e5e5e5` (light gray)
- Preview: `#4a9eff` (bright blue for path)

**Buttons:**
- Default button (Create): Blue `#3d5a99`
- Hover: Brighter
- Cancel: Standard gray

**Typography:**
- Title: 16px bold
- Labels: 11px normal
- Inputs: 11px
- Hints: 10px, `#666`
- Preview: 10px monospace

---

## 🔧 Technical Implementation

### File: `python/mono_tools/file_manager/ui/new_file_dialog.py`

**Class: `NewFileDialog(QtWidgets.QDialog)`**

**Constructor Parameters:**
```python
NewFileDialog(
    parent=None,
    type_name=None,         # Auto-fill from MiniBar
    department=None,        # Auto-fill from MiniBar
    subdepartment=None,     # Auto-fill from MiniBar
    username=None,          # Auto-detect
    is_assets=True,         # Asset or Shot mode
    asset_types=None,       # List of available types
    departments=None        # List of available departments
)
```

**Key Methods:**

**`_populate_fields()`** - Fill dropdowns with data
- Populate type combo from asset_types
- Populate department combo from departments
- Auto-select current values
- Trigger subdept update

**`_on_dept_changed()`** - Update subdept options
- Load subdepts for selected department
- Add "(None)" option
- Auto-select current subdept

**`_update_preview()`** - Update path preview
- Build path from current values
- Generate filename
- Show in preview label

**`_on_create()`** - Validate and accept
- Check all required fields
- Validate username format
- Accept dialog if valid

**`get_values()`** - Return all values
```python
{
    'type': ...,
    'department': ...,
    'subdepartment': ...,
    'username': ...,
    'name': ...
}
```

---

### File: `python/mono_tools/file_manager/file_manager_minibar.py`

**Updated `_new_file()` (line ~969-1157)**

**Before:**
```python
# Used hou.ui.readInput() - simple text input
result = hou.ui.readInput(prompt, ...)
```

**After:**
```python
# Use custom NewFileDialog
dialog = NewFileDialog(
    parent=self,
    type_name=self.current_type,
    department=self.current_dept,
    subdepartment=self.current_subdept,
    username=get_current_username(),
    ...
)

if dialog.exec_():
    values = dialog.get_values()
    # Use values...
```

---

## 🎯 Complete Workflow

### User Flow:

```
1. MiniBar selections:
   Type: Shots
   Dept: 02_sim → Crowd
   User: All

2. Click ⚡ → New File
   ↓
3. Dialog opens with auto-filled:
   ┌─────────────────────────┐
   │ Type:  [🎬 Shots     ▼] │ ← Auto-filled
   │ Dept:  [💨 02_sim    ▼] │ ← Auto-filled
   │ Subdept:[01_crowd    ▼] │ ← Auto-filled
   │ User:  [john          ] │ ← Auto-detected
   │ Name:  [            ] │ ← Empty (user input)
   │                        │
   │ Preview:               │
   │ 02_shots/02_sim/       │
   │  01_crowd/john/        │
   │  Shots__sim_v001.hip   │ ← Updates as you type
   └────────────────────────┘

4. User enters name: "Sh010"
   ↓
   Preview updates:
   02_shots/02_sim/01_crowd/john/Shots_Sh010_sim_v001.hip

5. User can change any field:
   - Change type → Dept options update
   - Change dept → Subdept options update
   - Change subdept → Preview updates
   - Change user → Preview updates
   - Change name → Preview updates

6. Click "Create File"
   ↓
   Validation:
   ✅ Type selected
   ✅ Department selected
   ✅ Username valid (lowercase, no \d{2}_ prefix)
   ✅ Name entered
   ↓
7. File created at preview path
8. User workspace auto-created
9. Activity registered
10. File appears in MiniBar list
```

---

## 📊 Comparison: Old vs New

### Old Dialog (hou.ui.readInput):
```
┌────────────────────────────────┐
│ Create new shot file:          │
│                                │
│ Type: Shots                    │
│ Department: 02_sim             │
│ Subdepartment: 01_crowd        │
│ User Workspace: john           │
│                                │
│ Enter shot name:               │
│ [                    ]         │
│                                │
│      [Create]  [Cancel]        │
└────────────────────────────────┘
```
- ❌ Read-only info, can't change
- ❌ Single text input only
- ❌ No preview
- ❌ Basic validation only

### New Dialog (NewFileDialog):
```
┌──────────────────────────────────────┐
│ Create New File                      │
│                                      │
│ Type:        [🎬 Shots           ▼] │
│ Department:  [💨 02_sim          ▼] │
│ Subdepartment:[01_crowd          ▼] │
│ User:        [john                ] │
│ Shot Name:   [Sh010               ] │
│                                      │
│ Preview:                             │
│ ┌──────────────────────────────────┐│
│ │ 02_shots/02_sim/01_crowd/john/...││
│ └──────────────────────────────────┘│
│                                      │
│          [Cancel]  [Create File]    │
└──────────────────────────────────────┘
```
- ✅ All fields editable
- ✅ Dropdowns with all options
- ✅ Real-time preview
- ✅ Full validation
- ✅ Auto-fill from selections
- ✅ Consistent UI styling

---

## 🎨 Future: New Folder Dialog (Same approach)

Would also create custom dialog for New Folder with:
- Asset type selection
- Asset name input
- Department checklist (select which to create)
- Subdepartment options shown
- Preview of full structure
- Create button

**Benefits:**
- Consistent UI
- Better UX
- More control
- Visual feedback

---

## ✅ Implementation Complete

**Files Created:**
- `python/mono_tools/file_manager/ui/new_file_dialog.py` - Custom dialog

**Files Modified:**
- `python/mono_tools/file_manager/ui/__init__.py` - Export NewFileDialog
- `python/mono_tools/file_manager/file_manager_minibar.py` - Use custom dialog

**Features:**
- ✅ Custom New File Dialog
- ✅ Auto-filled from MiniBar
- ✅ All fields editable
- ✅ Dynamic subdepartment dropdown
- ✅ Real-time path preview
- ✅ Full validation
- ✅ Consistent styling
- ✅ User workspace support

---

## 🧪 Quick Test

```python
# In Houdini:

# Restart Houdini first!

# Open MiniBar
from mono_tools import show_mono_minibar
show_mono_minibar()

# Make selections:
# 1. Type: Shots
# 2. Dept: 02_sim → Crowd

# Click ⚡ → New File

# Custom dialog opens with:
# - All fields pre-filled ✅
# - Can change any field ✅
# - Preview updates live ✅
# - Enter name and create ✅
```

---

**Ready for testing!** 🚀

**MonoStudio v2.3.0** - Complete!

**© 2024 MonoStudio**

