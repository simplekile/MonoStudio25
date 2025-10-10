# New Folder Workflow - User Simulation

## Overview

Giả lập chi tiết user workflow khi tạo asset folder mới với MiniBar.

---

## 🎬 Complete Workflow

### Step 0: Initial Setup
```
User đã configure:
  • Project Root: D:/Dropbox/Job
  • Current Project: 250724_grn_vp83
  • MiniBar đang chạy
```

---

### Step 1: Open Quick Menu
```
User action: Click ⚡ button

UI shows:
┌──────────────────────────┐
│ 📄 New File...           │
│ 📁 New Folder...         │ ← User clicks this
│ 💾 Save Version...       │
├──────────────────────────┤
│ 📂 Open File Location    │
│ 🎬 Open Render Folder    │
├──────────────────────────┤
│ 🔄 Reload Scene          │
│ 🔃 Restart Houdini       │
└──────────────────────────┘
```

---

### Step 2: Dialog 1 - Select Type
```
Code: Scans project → Finds available types

Dialog:
┌──────────────────────────────────────┐
│ New Folder - Select Type            │
├──────────────────────────────────────┤
│ Available types:                     │
│   • _characters                      │
│   • _props                           │
│   • _environments                    │
│                                      │
│ Enter type name:                     │
│ [_characters________________]        │
│                                      │
│            [Next]  [Cancel]          │
└──────────────────────────────────────┘

User enters: _characters
```

---

### Step 3: Dialog 2 - Enter Asset Name
```
Dialog:
┌──────────────────────────────────────┐
│ New Folder - Asset Name             │
├──────────────────────────────────────┤
│ Type: _characters                    │
│                                      │
│ Enter asset name:                    │
│ (e.g., Omega, Chair, Tree)           │
│                                      │
│ [Phoenix________________]            │
│                                      │
│          [Create]  [Cancel]          │
└──────────────────────────────────────┘

User enters: Phoenix
```

---

### Step 4: Code Processing
```
Code:
1. Type: _characters
2. Asset: Phoenix
3. Auto-prefix: char_Phoenix (added 'char_')
4. Load departments from config/department_structure.json:
   ✅ 01_modeling
   ✅ 02_rigging
   ✅ 03_surfacing
   ✅ 04_lookdev
   ✅ 05_groom
   ✅ 06_anim
   ✅ 07_turntable
```

---

### Step 5: Dialog 3 - Preview & Confirm
```
Dialog:
┌─────────────────────────────────────────────┐
│ Confirm Folder Structure                   │
├─────────────────────────────────────────────┤
│ Creating folder structure:                  │
│                                             │
│ 01_assets/_characters/char_Phoenix/         │
│   ├─ 01_modeling/                           │
│   ├─ 02_rigging/                            │
│   ├─ 03_surfacing/                          │
│   ├─ 04_lookdev/                            │
│   ├─ 05_groom/                              │
│   ├─ 06_anim/                               │
│   └─ 07_turntable/                          │
│                                             │
│ Total: 7 department folders                 │
│                                             │
│ Proceed?                                    │
│                                             │
│             [Create]  [Cancel]              │
└─────────────────────────────────────────────┘

User clicks: Create
```

---

### Step 6: Folder Creation
```
Code: create_asset_folder_structure()

Creating folders:
✅ D:/Dropbox/Job/250724_grn_vp83/01_assets/_characters/char_Phoenix/01_modeling/
✅ D:/Dropbox/Job/250724_grn_vp83/01_assets/_characters/char_Phoenix/02_rigging/
✅ D:/Dropbox/Job/250724_grn_vp83/01_assets/_characters/char_Phoenix/03_surfacing/
✅ D:/Dropbox/Job/250724_grn_vp83/01_assets/_characters/char_Phoenix/04_lookdev/
✅ D:/Dropbox/Job/250724_grn_vp83/01_assets/_characters/char_Phoenix/05_groom/
✅ D:/Dropbox/Job/250724_grn_vp83/01_assets/_characters/char_Phoenix/06_anim/
✅ D:/Dropbox/Job/250724_grn_vp83/01_assets/_characters/char_Phoenix/07_turntable/

All created successfully!
```

---

### Step 7: Success Message
```
Dialog:
┌─────────────────────────────────────────────┐
│ Folder Created                              │
├─────────────────────────────────────────────┤
│ Asset folder created successfully!          │
│                                             │
│ Asset: char_Phoenix                         │
│ Location:                                   │
│ .../01_assets/_characters/char_Phoenix      │
│                                             │
│ Departments created:                        │
│   • 01_modeling                             │
│   • 02_rigging                              │
│   • 03_surfacing                            │
│   • 04_lookdev                              │
│   • 05_groom                                │
│   • 06_anim                                 │
│   • 07_turntable                            │
│                                             │
│                   [OK]                      │
└─────────────────────────────────────────────┘
```

---

### Step 8: Create File Prompt (Optional)
```
Dialog:
┌─────────────────────────────────────────────┐
│ Create File?                                │
├─────────────────────────────────────────────┤
│ Folder structure created!                   │
│                                             │
│ Would you like to create a new file         │
│ in this asset?                              │
│                                             │
│                   [Yes]  [No]               │
└─────────────────────────────────────────────┘

If User clicks Yes:
  → Opens New File dialog
  → Type: _characters (auto-selected)
  → Name: Phoenix (suggested)
  → Department: Select from dropdown
  → File created: characters_Phoenix_modeling_v001.hip
```

---

## 📁 Result Structure

```
D:/Dropbox/Job/250724_grn_vp83/
└── 01_assets/
    └── _characters/
        └── char_Phoenix/              ← New asset folder
            ├── 01_modeling/           ← Ready for modeling files
            ├── 02_rigging/            ← Ready for rigging files
            ├── 03_surfacing/          ← Ready for surfacing files
            ├── 04_lookdev/            ← Ready for lookdev files
            ├── 05_groom/              ← Ready for groom files
            ├── 06_anim/               ← Ready for animation files
            └── 07_turntable/          ← Ready for turntable renders
```

---

## 🏷️ Naming Examples

### Example 1: Character Asset
```
Type: _characters
Name: Omega

Result:
  Folder: char_Omega
  Path: 01_assets/_characters/char_Omega/
  File: characters_Omega_modeling_v001.hip
```

### Example 2: Prop Asset
```
Type: _props
Name: MagicStaff

Result:
  Folder: prop_MagicStaff
  Path: 01_assets/_props/prop_MagicStaff/
  File: props_MagicStaff_surfacing_v001.hip
```

### Example 3: Environment Asset
```
Type: _environments
Name: ForestPath

Result:
  Folder: env_ForestPath
  Path: 01_assets/_environments/env_ForestPath/
  File: environments_ForestPath_lookdev_v001.hip
```

---

## 🔧 Technical Details

### Auto-Prefixing Logic
```python
if 'character' in type_name.lower():
    prefix = 'char_'
elif 'prop' in type_name.lower():
    prefix = 'prop_'
elif 'environment' in type_name.lower():
    prefix = 'env_'

folder_name = f"{prefix}{asset_name}"
```

### Department Loading
```python
# From config/department_structure.json
departments = get_standard_departments()
# Returns: ["01_modeling", "02_rigging", ...]
```

### Folder Creation
```python
for dept in departments:
    dept_path = os.path.join(asset_folder, dept)
    os.makedirs(dept_path, exist_ok=True)
```

---

## ⏱️ Timing

| Step | Duration | Note |
|------|----------|------|
| Click ⚡ | <1ms | Instant |
| Click New Folder | <1ms | Instant |
| Type selection | <50ms | Scan project |
| Name input | User time | Interactive |
| Preview | <1ms | Instant |
| Create folders | 10-50ms | Disk I/O |
| Success message | <1ms | Instant |

**Total:** ~100ms + user input time

---

## 💡 Tips

### Quick Workflow
```
1. ⚡ → New Folder
2. Type: _characters (or press Enter for last used)
3. Name: AssetName
4. Confirm
5. Done!
```

### Batch Creation
```
Create multiple assets quickly:
- Workflow is sticky (remembers type)
- Each asset takes ~30 seconds
- Perfect for batch setup
```

### File Creation After
```
After folder creation:
  → Click "Yes" to create first file
  → Opens New File dialog with type pre-selected
  → Department dropdown ready
  → Quick start!
```

---

## 🎯 Summary

**Total clicks:** 4-5 clicks
**Total time:** 30-60 seconds
**Result:** Complete asset structure ready for production

**Comparison:**

| Method | Time | Consistency | Errors |
|--------|------|-------------|--------|
| Manual creation | 5-10 min | Low | High |
| New Folder feature | 30 sec | High | None |

**Efficiency gain:** 10-20x faster! 🚀

---

**Version:** 2.2.0
**Last Updated:** 2024-12-19

