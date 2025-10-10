# Pipeline Tools Analysis - Folder Structure Tab

## Current Implementation (MonoStudio v2.2.0)

### What We Have:
```
🏗️ Project Structure Tab
├─ Template dropdown (Default, Simple, Custom)
├─ Preview area (read-only text)
├─ Customize button → Advanced dialog
└─ Apply Template button
```

### Features:
- ✅ Template selection
- ✅ Visual preview
- ✅ Save/apply
- ✅ Custom editing (basic)

---

## Professional Pipeline Tools Comparison

### 1. **ftrack Studio**
```
Project Schema Editor:
├─ Asset Types
│  ├─ Character
│  ├─ Prop
│  └─ Environment
├─ Task Templates
│  ├─ Modeling → [Sculpt, Retopo, UV]
│  ├─ Rigging
│  └─ Surfacing → [Texture, LookDev]
└─ Folder Structure Schema
   ├─ Template preview (live)
   ├─ Variables: {asset_type}/{asset_name}/{task}
   └─ Rules & Validation
```

**Key Features:**
- Hierarchical template system
- Asset types + Task breakdown
- Variable-based paths
- Validation rules
- Version control for schemas

---

### 2. **ShotGrid (Autodesk)**
```
File System Schema:
├─ Schema Tree (Visual hierarchy)
│  ├─ Project
│  │  ├─ Assets
│  │  │  └─ {asset_type}
│  │  │     └─ {asset_name}
│  │  │        └─ {pipeline_step}
│  │  └─ Shots
├─ Path Expressions
├─ Folder Creation Rules
└─ Template Preview + Validation
```

**Key Features:**
- Visual tree editor (drag & drop)
- Token/variable system
- Conditional folder creation
- Per-entity customization
- Multi-OS path handling

---

### 3. **Prism Pipeline**
```
Project Settings → Folder Structure:
├─ Entity Types (Assets, Shots)
├─ Step Templates
│  ├─ Add/Remove/Reorder
│  ├─ Abbreviations (mdl, rig, srf)
│  └─ Software per step
├─ Folder Naming Convention
└─ Export/Import Templates
```

**Key Features:**
- Step abbreviations
- Software integration
- Template export/import
- Department-specific settings
- Version/publish structure

---

### 4. **Kitsu / Zou (CGWire)**
```
Project Structure:
├─ Asset Types (predefined + custom)
├─ Task Types (art, modeling, rigging...)
├─ File Tree Template
│  └─ Folder + File naming patterns
└─ Working/Output separation
```

**Key Features:**
- Predefined industry templates
- Custom task types
- Naming patterns
- Working vs Output folders
- Metadata integration

---

## Gap Analysis: What We're Missing

### ❌ Missing Features:

#### 1. **Visual Hierarchy Editor**
Current: Text preview only
Industry: Tree view, drag & drop

#### 2. **Variable/Token System**
Current: Hardcoded structure
Industry: `{asset_type}/{asset}/{dept}/{version}`

#### 3. **Per-Department Software Config**
Current: Global software list
Industry: Per-task software assignment

#### 4. **Validation & Rules**
Current: None
Industry: Folder name validation, required fields

#### 5. **Asset Type Management**
Current: Separate section in JSON
Industry: Integrated with folder structure

#### 6. **Subdepartment Support**
Current: None
Industry: Modeling → Sculpt, Retopo, UV (from your template!)

#### 7. **Template Library**
Current: 3 hardcoded templates
Industry: Import/export, share templates

#### 8. **Naming Conventions**
Current: Hardcoded `Hero_` prefix
Industry: Configurable patterns per type

#### 9. **Version & Publish Structure**
Current: Simple `_publish/` folder
Industry: `work/`, `publish/`, `review/` with version patterns

#### 10. **Multi-Project Templates**
Current: One config for all
Industry: Per-project templates

---

## Recommendations (Priority Order)

### 🔴 CRITICAL (Should Have)

#### 1. **Integrate Asset Types into Structure Tab**
Currently separate in config → Should be in UI

**Proposed:**
```
🏗️ Project Structure
├─ Asset Types Section
│  ├─ List: _characters, _props, _environments
│  └─ [Add] [Edit] [Remove]
└─ Folder Structure Section
   ├─ Template dropdown
   └─ Preview
```

#### 2. **Add Subdepartment Support**
Match your actual template structure!

**Example:**
```
01_modeling/
├─ 01_sculpt/ (subdepartment)
├─ 02_retopo/ (subdepartment)
├─ 03_uv/ (subdepartment)
└─ _publish/
```

#### 3. **Per-Department Software Config in UI**
Currently only in JSON → Add to Customize dialog

**Proposed Edit Dialog:**
```
Edit Department: 01_modeling
├─ Name: [Modeling____]
├─ Icon: [🎨]
├─ Software:
│  ☑ Houdini
│  ☑ Maya
│  ☑ ZBrush
│  ☐ Blender
├─ Create Publish: ☑
└─ Subdepartments:
   ├─ 01_sculpt (+ publish)
   ├─ 02_retopo (+ publish)
   └─ 03_uv
```

---

### 🟡 IMPORTANT (Nice to Have)

#### 4. **Tree View Preview**
Replace text with interactive tree

```
Example: Hero_Phoenix/
└─ 01_modeling/          [▼]
   ├─ houdini/
   ├─ maya/
   ├─ zbrush/
   ├─ 01_sculpt/         [▼]
   │  └─ _publish/
   ├─ 02_retopo/
   └─ _publish/
```

#### 5. **Template Import/Export**
Share templates between projects/users

#### 6. **Naming Pattern Editor**
Configure prefixes per asset type

```
Asset Type: _characters
Prefix Pattern: Hero_
Example: Hero_Phoenix
```

---

### 🟢 FUTURE (Advanced)

#### 7. **Variable System**
`{project}/{asset_type}/{asset_name}/{dept}/{version}`

#### 8. **Validation Rules**
- Allowed characters
- Name length limits
- Reserved words

#### 9. **Version Structure Config**
```
Work Files: work/
Publish: publish/
Review: review/
```

---

## Proposed UI Redesign

### Option A: Split into 2 Sub-Tabs

```
🏗️ Project Structure
├─ [Asset Types] [Folder Structure]
│
├─ Asset Types Tab:
│  ├─ List of types
│  ├─ Add/Edit/Remove
│  └─ Prefix configuration
│
└─ Folder Structure Tab:
   ├─ Template dropdown
   ├─ Visual tree preview
   └─ Customize → Full editor
```

### Option B: Unified View (Recommended)

```
🏗️ Project Structure
├─ Asset Types
│  ├─ [_characters] [_props] [_environments] [+]
│  └─ Selected: _characters (Hero_ prefix)
│
├─ Department Structure
│  ├─ Template: [Default ▼]
│  └─ Tree Preview:
│     └─ Example: Hero_Phoenix/
│        ├─ 01_modeling/
│        │  ├─ [+] houdini/
│        │  ├─ [+] maya/
│        │  └─ [+] _publish/
│        ├─ 02_rigging/
│        └─ ...
│
└─ [✏️ Edit Structure] [💾 Save]
```

---

## Implementation Priority

### Phase 1: Essential Fixes (Now)
1. Add Asset Type management to UI
2. Add software checkboxes to Edit dialog
3. Add subdepartment support

### Phase 2: Better UX (Next)
4. Tree view preview
5. Better edit dialog layout
6. Template import/export

### Phase 3: Advanced (Future)
7. Variable system
8. Validation rules
9. Multi-project templates

---

## Comparison Score

| Feature | MonoStudio | ftrack | ShotGrid | Prism | Kitsu |
|---------|-----------|--------|----------|-------|-------|
| Template Selection | ✅ 3 | ✅ Many | ✅ Custom | ✅ Many | ✅ Presets |
| Visual Preview | ⚠️ Text | ✅ Live | ✅ Tree | ✅ List | ⚠️ Text |
| Custom Edit | ⚠️ Basic | ✅ Full | ✅ Full | ✅ Full | ⚠️ Basic |
| Asset Types | ⚠️ JSON | ✅ UI | ✅ UI | ✅ UI | ✅ UI |
| Subdepartments | ❌ No | ✅ Yes | ✅ Yes | ⚠️ Partial | ❌ No |
| Software Config | ⚠️ JSON | ✅ UI | ✅ UI | ✅ UI | ⚠️ JSON |
| Variables | ❌ No | ✅ Yes | ✅ Yes | ⚠️ Partial | ⚠️ Partial |
| Validation | ❌ No | ✅ Yes | ✅ Yes | ⚠️ Partial | ❌ No |
| Import/Export | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |

**Score: 4/10** (Functional but basic)

---

## Conclusion

**Current State:** 
- ✅ Works for basic use case
- ⚠️ Missing key professional features
- ❌ Not as flexible as industry tools

**To Reach Professional Level:**
1. Integrate Asset Types into UI
2. Add subdepartment support (match template!)
3. Visual tree editor for structure
4. Better customize dialog with checkboxes
5. Template sharing system

**Priority:** Focus on Phase 1 - these are table stakes for professional pipelines.

