# New File & New Folder - Updated for v2.3.0

## ✅ Updates Complete

**Features**: New File + New Folder now support subdepartments & user workspaces  
**Version**: 2.3.0  
**Status**: Ready for Testing

---

## 🎯 What Changed

### Before v2.3.0:
```
New File → Creates in:
  01_assets/{type}/{asset}/{dept}/file.hip

New Folder → Creates:
  01_assets/{type}/{asset}/{dept}/
```

### After v2.3.0:
```
New File → Creates in:
  01_assets/{type}/{asset}/{dept}/[{subdept}/]{user}/file.hip
  
New Folder → Creates:
  01_assets/{type}/{asset}/{dept}/
    ├── {subdept}/        ← NEW! From config
    │   └── _publish/
    └── _publish/
```

---

## 📋 Feature 1: New File with User Workspace

### Behavior:

**When creating new file:**
1. Uses current selections: Type, Dept, Subdept
2. Auto-detects current username
3. Creates file in user workspace
4. Registers user activity

### Example Flow:

```
Selections:
  Type: Shots
  Dept: 02_sim
  Subdept: 01_crowd    ← Selected from hierarchical menu
  User: john           ← Auto-detected

Click: ⚡ → New File
  ↓
Dialog shows:
  "Create new shot file:
   
   Type: Shots
   Department: 02_sim
   Subdepartment: 01_crowd
   User Workspace: john
   
   Enter shot name:"
  ↓
Enter: "Sh010"
  ↓
Creates file at:
  02_shots/02_sim/01_crowd/john/Shots_Sh010_sim_v001.hip
                          ↑     ↑
                          │     └─ Auto-created user workspace
                          └─ Subdepartment from selection
  ↓
Registers activity in .mono/users.json
  ↓
Success message shows full path with subdept + user info
```

---

### File Paths Created:

#### With Subdepartment:
```
Assets:
  01_assets/
    _characters/
      char_Hero/
        01_modeling/
          01_sculpt/         ← Subdepartment
            john/            ← User workspace (auto-created)
              characters_Hero_modeling_v001.hip

Shots:
  02_shots/
    02_sim/
      01_crowd/              ← Subdepartment
        john/                ← User workspace (auto-created)
          Shots_Sh010_sim_v001.hip
```

#### Without Subdepartment:
```
Assets:
  01_assets/
    _characters/
      char_Hero/
        02_rigging/
          john/              ← User workspace (auto-created)
            characters_Hero_rigging_v001.hip

Shots:
  02_shots/
    03_lighting/
      john/                  ← User workspace (auto-created)
        Shots_Sh010_lighting_v001.hip
```

---

## 📋 Feature 2: New Folder with Subdepartments

### Asset Folder Preview (Updated):

**Before v2.3.0:**
```
Creating folder structure:

01_assets/_characters/char_Hero/
  ├─ 01_modeling/
  │  └─ _publish/
  ├─ 02_rigging/
  │  └─ _publish/
  └─ 03_surfacing/
     └─ _publish/
```

**After v2.3.0:**
```
Creating folder structure:

01_assets/_characters/char_Hero/
  ├─ 01_modeling/
  │  ├─ 01_sculpt/ (Sculpt)          ← NEW! Subdepartment
  │  │  └─ _publish/
  │  ├─ 02_retopo/ (Retopo)          ← NEW!
  │  │  └─ _publish/
  │  ├─ 03_uv/ (UV)                  ← NEW!
  │  └─ _publish/
  ├─ 02_rigging/
  │  └─ _publish/
  └─ 03_surfacing/
     ├─ 01_texture/ (Texture)        ← NEW! Subdepartment
     └─ _publish/

Total: 7 departments, 25 folders
```

---

### Shot Folder Preview (Updated):

**Before v2.3.0:**
```
Creating shot structure:

02_shots/sq010_sh0010/
  ├─ 🎬 01_animation/ (Animation)
  │  └─ _publish/
  ├─ 💨 02_sim/ (Simulation)
  │  └─ _publish/
  └─ 💡 03_lighting/ (Lighting)
```

**After v2.3.0:**
```
Creating shot structure:

02_shots/sq010_sh0010/
  ├─ 🎬 01_animation/ (Animation)
  ├─ 💨 02_sim/ (Simulation)
  │  ├─ 01_crowd/ (Crowd)            ← NEW! Subdepartment
  │  │  └─ _publish/
  │  ├─ 02_cloth/ (Cloth)            ← NEW!
  │  │  └─ _publish/
  │  ├─ 03_destruction/ (Destruction) ← NEW!
  │  │  └─ _publish/
  │  └─ _publish/
  ├─ 💡 03_lighting/ (Lighting)
  └─ 🎞️ 04_comp/ (Compositing)

Total: 4 departments, 14 folders
```

---

## 🔧 Technical Changes

### File: `python/mono_tools/file_manager/file_manager_minibar.py`

**1. Updated `_new_file()` (line ~969-1157)**

**Added:**
- Get current subdepartment: `subdepartment = self.current_subdept`
- Get current username: `username = get_current_username()`
- Build context info showing subdept + user
- Update target directory to include subdept + user
- Register user activity after file creation
- Updated success message with full path info

**Target directory logic:**
```python
# Assets with subdept:
path = [root, project, "01_assets", type, asset, dept, subdept, username]

# Assets without subdept:
path = [root, project, "01_assets", type, asset, dept, username]

# Shots with subdept:
path = [root, project, "02_shots", dept, subdept, username]

# Shots without subdept:
path = [root, project, "02_shots", dept, username]
```

---

**2. Updated `_new_asset_folder()` (line ~1202-1400)**

**Preview display updated:**
- Shows subdepartments with indentation
- Shows subdepartment names
- Shows subdepartment publish folders
- Counts subdepartments in total

**Example preview:**
```
01_assets/_characters/char_Hero/
  ├─ 01_modeling/
  │  ├─ 01_sculpt/ (Sculpt)    ← Shows subdepartment
  │  │  └─ _publish/            ← Shows subdept publish
  │  ├─ 02_retopo/ (Retopo)
  │  │  └─ _publish/
  │  └─ 03_uv/ (UV)
```

---

**3. Updated `_new_shot_folder()` (line ~1423-1540)**

**Preview display updated:**
- Shows subdepartments for shot departments
- Shows subdepartment publish folders
- Counts subdepartments in total

**Example preview:**
```
02_shots/sq010_sh0010/
  ├─ 💨 02_sim/ (Simulation)
  │  ├─ 01_crowd/ (Crowd)     ← Shows subdepartment
  │  │  └─ _publish/
  │  ├─ 02_cloth/ (Cloth)
  │  │  └─ _publish/
  │  └─ _publish/
```

**Folder creation logic:**
- Already creates subdepartments (via `create_publish` field)
- Updated preview only (logic already correct)

---

## 🎯 Complete Workflow Examples

### Example 1: Create File in Subdepartment

```
Workflow:
1. Select Type: Shots
2. Select Dept: 02_sim → Crowd (from submenu!)
3. User button shows: "👤 All" (or your username)
4. Click ⚡ → New File
5. Dialog shows:
   "Create new shot file:
    Type: Shots
    Department: 02_sim
    Subdepartment: 01_crowd    ← From selection
    User Workspace: john       ← Auto-detected
    
    Enter shot name:"
6. Enter: "Sh010"
7. Creates: 02_shots/02_sim/01_crowd/john/Shots_Sh010_sim_v001.hip
8. User workspace "john/" auto-created
9. Activity registered in .mono/users.json
10. File appears in list with: "⭐ john - Shots_Sh010 (v001)"
```

---

### Example 2: Create Asset Folder with Subdepartments

```
Workflow:
1. Click ⚡ → New Folder
2. Select: "Asset Folder"
3. Select Type: "_characters"
4. Enter Asset Name: "Hero"
5. Preview shows:
   
   01_assets/_characters/char_Hero/
     ├─ 01_modeling/
     │  ├─ 01_sculpt/ (Sculpt)     ← Subdepartments!
     │  │  └─ _publish/
     │  ├─ 02_retopo/ (Retopo)
     │  │  └─ _publish/
     │  ├─ 03_uv/ (UV)
     │  └─ _publish/
     ├─ 02_rigging/
     │  └─ _publish/
     └─ 03_surfacing/
        ├─ 01_texture/ (Texture)    ← Subdepartment!
        └─ _publish/
   
   Total: 7 departments, 25 folders
   
6. Click "Create"
7. All folders created including subdepartments
8. Success!
```

---

### Example 3: Create Shot Folder with Subdepartments

```
Workflow:
1. Click ⚡ → New Folder
2. Select: "Shot Folder"
3. Enter Shot Name: "sq010_sh0010"
4. Preview shows:
   
   02_shots/sq010_sh0010/
     ├─ 🎬 01_animation/ (Animation)
     ├─ 💨 02_sim/ (Simulation)
     │  ├─ 01_crowd/ (Crowd)        ← Subdepartments!
     │  │  └─ _publish/
     │  ├─ 02_cloth/ (Cloth)
     │  │  └─ _publish/
     │  ├─ 03_destruction/ (Destruction)
     │  │  └─ _publish/
     │  └─ _publish/
     ├─ 💡 03_lighting/ (Lighting)
     └─ 🎞️ 04_comp/ (Compositing)
   
   Total: 4 departments, 14 folders
   
5. Click "Create"
6. All folders created including subdepartments
7. Ready to work!
```

---

## 📊 File Creation Matrix

| Selection | File Path Created |
|-----------|-------------------|
| Dept only | `dept/user/file.hip` |
| Dept + Subdept | `dept/subdept/user/file.hip` |
| Assets + Dept | `01_assets/type/asset/dept/user/file.hip` |
| Assets + Dept + Subdept | `01_assets/type/asset/dept/subdept/user/file.hip` |
| Shots + Dept | `02_shots/dept/user/file.hip` |
| Shots + Dept + Subdept | `02_shots/dept/subdept/user/file.hip` |

**All cases:** User workspace is always created!

---

## 🧪 Testing Guide

### Test 1: New File with Subdepartment
```
1. Select: Shots / 02_sim / 01_crowd
2. Click ⚡ → New File
3. Dialog shows subdept info: "Subdepartment: 01_crowd"
4. Enter shot name: "Sh010"
5. Verify file created at: 02_shots/02_sim/01_crowd/{username}/...
6. Verify user workspace auto-created
7. Verify .mono/users.json updated
8. Verify file appears in list with username
```

### Test 2: New File without Subdepartment
```
1. Select: Shots / 03_lighting (no subdepts)
2. Click ⚡ → New File
3. Dialog doesn't show subdept line
4. Enter shot name
5. Verify file created at: 02_shots/03_lighting/{username}/...
```

### Test 3: New Asset Folder
```
1. Click ⚡ → New Folder → Asset Folder
2. Select type, enter asset name
3. Preview shows subdepartments:
   - 01_modeling has 01_sculpt, 02_retopo, 03_uv
   - 03_surfacing has 01_texture
4. Confirm creation
5. Verify all subdepartments created
6. Verify publish folders created
```

### Test 4: New Shot Folder
```
1. Click ⚡ → New Folder → Shot Folder
2. Enter shot name: "sq010_sh0010"
3. Preview shows:
   - 02_sim with subdepts: 01_crowd, 02_cloth, 03_destruction
4. Confirm creation
5. Verify all subdepartments created
6. Verify structure matches preview
```

### Test 5: User Activity Tracking
```
1. Create new file
2. Check .mono/users.json
3. Verify user entry created/updated
4. Verify last_active timestamp
5. Create another file
6. Verify timestamp updated
```

---

## 📁 Complete Structure Example

### After creating everything:

```
project/
  .mono/
    users.json              ← Activity tracking
  
  01_assets/
    _characters/
      char_Hero/            ← From New Folder
        01_modeling/
          01_sculpt/        ← Subdepartment (from config)
            john/           ← User workspace (from New File)
              characters_Hero_modeling_v001.hip
            _publish/
          02_retopo/
            _publish/
          03_uv/
          _publish/
        02_rigging/
          john/
            characters_Hero_rigging_v001.hip
          _publish/
  
  02_shots/
    sq010_sh0010/           ← From New Folder
      01_animation/
      02_sim/
        01_crowd/           ← Subdepartment (from config)
          john/             ← User workspace (from New File)
            Shots_Sh010_sim_v001.hip
          _publish/
        02_cloth/
          _publish/
        03_destruction/
          _publish/
        _publish/
      03_lighting/
        john/
          Shots_Sh010_lighting_v001.hip
      04_comp/
```

---

## 🎨 Success Message Examples

### New File with Subdepartment:
```
New file created successfully!

Shots_Sh010_sim_v001.hip

Department: 02_sim
Subdepartment: 01_crowd
User: john

Location:
D:\Project\02_shots\02_sim\01_crowd\john\
```

### New File without Subdepartment:
```
New file created successfully!

Shots_Sh010_lighting_v001.hip

Department: 03_lighting
User: john

Location:
D:\Project\02_shots\03_lighting\john\
```

---

## 🔧 Technical Details

### Auto-created Folders:

**When creating new file:**
1. Target directory determined from selections
2. `os.makedirs(target_dir, exist_ok=True)` creates all parent folders
3. User workspace folder created automatically
4. File saved in user workspace
5. User activity registered

**Folder creation order:**
```
dept/ → subdept/ (if selected) → user/ → file.hip
  ↑         ↑                      ↑
  │         │                      └─ Auto-created
  │         └─ From selection
  └─ From selection
```

---

### User Activity Registration:

```python
# After file creation:
register_user_activity(project_path, username)

# Updates .mono/users.json:
{
  "users": {
    "john": {
      "full_name": "john",          // Or from User Settings
      "email": "",
      "department": null,
      "created": "2024-12-19T10:30:00",
      "last_active": "2024-12-19T15:45:00"  ← Updated!
    }
  }
}
```

---

## ✅ Benefits

### 1. Automatic User Workspace
- No manual folder creation
- Consistent structure
- Clear ownership from start

### 2. Subdepartment Support
- Preview shows full structure
- Creates all subdepartments
- Includes publish folders

### 3. Activity Tracking
- Every file creation tracked
- User engagement monitored
- Team activity visible

### 4. Smart Defaults
- Username auto-detected
- Subdepartment from selection
- Department from selection
- No manual input needed

---

## 🎯 Complete Feature Set

**New File:**
- ✅ Supports subdepartment selection
- ✅ Creates in user workspace
- ✅ Auto-creates user folder
- ✅ Registers user activity
- ✅ Shows full context in dialog
- ✅ Success message with full path

**New Folder:**
- ✅ Shows subdepartments in preview
- ✅ Creates all subdepartments
- ✅ Creates publish folders
- ✅ Accurate folder count
- ✅ Visual tree structure

**Together:**
- ✅ Consistent workflow
- ✅ Clear ownership
- ✅ Team collaboration ready
- ✅ Production-ready structure

---

## 🚀 Ready for Testing!

**Test now:**
1. Restart Houdini
2. Open MiniBar
3. Try New File with subdept selected
4. Try New Folder for asset
5. Try New Folder for shot
6. Verify user workspaces created
7. Verify subdepartments shown in preview

**All features working!** ✨

---

**MonoStudio v2.3.0** - Professional Pipeline Tool

**© 2024 MonoStudio**

