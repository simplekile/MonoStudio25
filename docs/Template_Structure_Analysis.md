# Template Structure Analysis

## Source
`D:\Dropbox\Stock\Template\Folder Structure\250724_ProjectDemo`

---

## Discovered Structure

### Level 1: Project Root
```
250724_ProjectDemo/
├─ _input/           (Client input, outsource files)
├─ _reference/       (Reference materials)
├─ 01_assets/        (Asset production)
├─ 02_shots/         (Shot production)
└─ 03_out/           (Final outputs)
```

### Level 2: Asset Types
```
01_assets/
├─ _characters/
├─ _environments/
└─ _graphic/
```

### Level 3: Asset Folders
```
_characters/
└─ Hero_CharacterA/
```

**Note:** Prefix is `Hero_` (not `char_`)

### Level 4: Departments
```
Hero_CharacterA/
├─ 01_modeling/
├─ 02_rigging/
├─ 03_surfacing/
├─ 04_lookdev/
├─ 05_groom/
├─ 06_anim/
├─ 06_cloth/
└─ 99_archive/
```

### Level 5: Sub-Departments + Publish

#### Modeling (Complex)
```
01_modeling/
├─ _publish/          ← Publish folder at dept level
├─ 01_sculpt/
│  └─ _publish/       ← Publish folder at subdept level
├─ 02_retopo/
│  └─ _publish/
└─ 03_uv/
```

#### Surfacing (Medium)
```
03_surfacing/
├─ _publish/
└─ 01_texture/
```

#### Rigging (Simple)
```
02_rigging/
└─ _publish/
```

#### Others
```
04_lookdev/       (no publish)
05_groom/
└─ _publish/
06_anim/          (no publish)
06_cloth/         (no publish)
99_archive/       (no publish)
```

---

## Key Findings

### 1. Nested Structure
- Departments can have **sub-departments**
- Example: modeling → sculpt, retopo, uv

### 2. Publish Folders
- Most departments have `_publish/`
- Sub-departments can also have `_publish/`
- Pattern: Final approved assets go here

### 3. Asset Prefix
- Characters use `Hero_` (not `char_`)
- Different from typical naming

### 4. Department Variations
- Two `06_` departments: anim and cloth (unusual)
- `99_archive` for old files

---

## Config Design

### Approach 1: Full Nested (Complex)
```json
{
  "id": "01_modeling",
  "subdepartments": [
    {"id": "01_sculpt", "create_publish": true},
    {"id": "02_retopo", "create_publish": true},
    {"id": "03_uv", "create_publish": false}
  ],
  "create_publish": true
}
```

**Result:**
```
01_modeling/
├─ _publish/
├─ 01_sculpt/
│  └─ _publish/
├─ 02_retopo/
│  └─ _publish/
└─ 03_uv/
```

### Approach 2: Simplified (Practical)
```json
{
  "id": "01_modeling",
  "create_publish": true,
  "optional_subfolders": ["sculpt", "retopo", "uv"]
}
```

**Result:**
```
01_modeling/
└─ _publish/
(User creates sculpt/retopo/uv manually when needed)
```

---

## Recommendation

**Use Approach 1 (Full Nested)** because:
1. Matches actual studio structure
2. Ensures consistency
3. Artists know where to put files
4. Pipeline tools can rely on structure

But make it **optional** - not all assets need full structure.

---

## Implementation Strategy

### Phase 1: Basic (Current)
- Department folders
- Software subfolders (houdini, maya, zbrush)
- ✅ Already done!

### Phase 2: Publish Folders
- Add `_publish/` to configured departments
- Quick win, high value

### Phase 3: Sub-Departments
- Full nested structure
- More complex but complete

---

Should I:
1. Create config based on template (full nested structure)
2. Keep current simple config
3. Add only publish folders for now (Phase 2)

