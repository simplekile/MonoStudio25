# New File Feature Guide

## Overview

MiniBar now has a "New File" button (📄) that creates new asset/shot files with automatic naming and folder creation.

---

## How to Use

### 1. Select Type & Department
```
1. Click 🏷️ Type → Select type (e.g., _characters)
2. Click 📁 Dept → Select department (e.g., 01_modeling)
```

### 2. Click New Button
```
3. Click 📄 button → Opens "New File" dialog
```

### 3. Enter Name
```
4. Enter asset/shot name (e.g., "Cyborg")
5. Click "Create"
```

### 4. Result
```
→ File created: characters_Cyborg_modeling_v001.hip
→ Folder created if needed
→ File opened in Houdini
→ File list refreshed
```

---

## Auto-Naming Format

### Format
```
$type_$assetname_$department_$version.ext
```

### Name Cleaning Rules

**Type:** Remove underscore prefix
```
_characters → characters
_environments → environments
_props → props
```

**Asset Name:** Remove prefix (char_, prop_, env_, etc.)
```
char_Cyborg → Cyborg
prop_Chair → Chair
env_Forest → Forest
```

**Department:** Remove number prefix
```
01_modeling → modeling
02_rigging → rigging
03_surfacing → surfacing
04_lookdev → lookdev
```

### Examples

#### Example 1: Character Modeling
```
Input:
  Type: _characters
  Asset: Cyborg
  Department: 01_modeling

Output:
  Filename: characters_Cyborg_modeling_v001.hip
  Path: 01_assets/_characters/char_Cyborg/01_modeling/
```

#### Example 2: Prop Surfacing
```
Input:
  Type: _props
  Asset: Chair
  Department: 03_surfacing

Output:
  Filename: props_Chair_surfacing_v001.hip
  Path: 01_assets/_props/prop_Chair/03_surfacing/
```

#### Example 3: Shot Lighting
```
Input:
  Type: Shots
  Shot: Sh010
  Department: 03_lighting

Output:
  Filename: Shots_Sh010_lighting_v001.hip
  Path: 02_shots/03_lighting/
```

---

## Automatic Folder Creation

### Assets Structure
```
01_assets/
└── _characters/
    └── char_Cyborg/        ← Created if not exists
        └── 01_modeling/    ← Created if not exists
            └── characters_Cyborg_modeling_v001.hip
```

### Shots Structure
```
02_shots/
└── 03_lighting/            ← Created if not exists
    └── Shots_Sh010_lighting_v001.hip
```

---

## Asset Prefix Auto-Detection

If you enter asset name **without prefix**, it's automatically added:

```
Type: _characters + Name: "Cyborg"
→ Folder: char_Cyborg (auto-prefixed)
→ Filename: characters_Cyborg_modeling_v001.hip

Type: _props + Name: "Chair"
→ Folder: prop_Chair (auto-prefixed)
→ Filename: props_Chair_surfacing_v001.hip
```

**Mapping:**
- _characters → char_
- _props → prop_
- _environments → env_

---

## Error Handling

### File Already Exists
```
Dialog: "File already exists. Open it instead?"
  → Yes: Opens existing file
  → No: Cancel operation
```

### Unsaved Changes
```
Dialog: "Save current scene before creating new?"
  → Save & Create: Saves then creates new
  → Create Without Saving: Creates new (loses changes)
  → Cancel: Abort operation
```

### No Type/Department
```
Error: "Please select a type first"
→ Click 🏷️ Type button
```

### No Project Configured
```
Error: "No project configured"
→ Click ⚙️ Settings to configure
```

---

## UI Location

### MiniBar Layout
```
⋮⋮ | 🏷️ Type | 📁 Dept | [Shot Display] | 📄 | ⚡ | 💾 | ⚙️
                                            ↑
                                         New button
```

---

## Features

### 1. Smart Naming
- Cleans type/asset/department names
- Removes numbers and underscores
- Consistent format

### 2. Auto-Folder Creation
- Creates full directory structure
- Handles missing intermediate folders
- Safe: uses os.makedirs(exist_ok=True)

### 3. Version Management
- Always starts at v001
- Can increment later with 💾 button
- Version format: v001, v002, etc.

### 4. Integration
- Opens file in Houdini immediately
- Refreshes MiniBar file list
- Status message confirmation

---

## Code Functions

### Helper Functions (file_manager_helpers.py)

```python
clean_type_name(type_name)
  _characters → characters

clean_department_name(dept_name)
  01_modeling → modeling

clean_asset_name(asset_name)
  char_Cyborg → Cyborg

generate_new_filename(type_name, asset_name, department, version, ext)
  → characters_Cyborg_modeling_v001.hip
```

### MiniBar Function

```python
_new_file()
  1. Validate type & department selected
  2. Prompt for asset/shot name
  3. Generate filename
  4. Create folder structure
  5. Create & open new file
  6. Refresh file list
```

---

## Workflow Example

### Creating Character Model

```
1. MiniBar shows: 🏷️ Type | 📁 Dept
2. Click 🏷️ → Select "_characters"
3. Click 📁 → Select "01_modeling"
4. Click 📄 → Dialog opens
5. Enter "Omega"
6. Click "Create"

Result:
✅ Folder: 01_assets/_characters/char_Omega/01_modeling/
✅ File: characters_Omega_modeling_v001.hip
✅ Opened in Houdini
✅ MiniBar refreshed
```

---

## Tips

### Quick Workflow
```
Type + Dept selection is sticky
→ Create multiple files for same type/dept without re-selecting
```

### Naming Convention
```
Use clean names: "Cyborg" not "char_Cyborg"
System adds prefixes automatically
```

### Version Control
```
Start: v001 (New File)
Save: v002, v003... (Save Version button)
```

---

## Technical Details

### File Extension
- Default: `.hip` (Houdini binary)
- Can be changed in code to `.hipnc` or `.hiplc`

### Version Format
- Pattern: `v###` (3 digits)
- Start: v001
- Increment: handled by Save Version feature

### Folder Structure
**Assets:**
```
01_assets/$type/$prefix_$name/$department/
```

**Shots:**
```
02_shots/$department/
```

---

**Version:** 2.2.0
**Last Updated:** 2024-12-19
**Status:** Production Ready

