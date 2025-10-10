# Version Update Checklist

## 🎯 Khi Nào Cần Update Version?

### MAJOR (x.0.0)
- Breaking changes
- API changes không tương thích ngược
- Thay đổi cấu trúc project lớn

### MINOR (x.y.0)
- New features
- Significant refactoring (như simplified startup)
- Thêm/xóa files quan trọng
- Thay đổi behavior đáng kể

### PATCH (x.y.z)
- Bug fixes
- Minor improvements
- Documentation updates
- Performance tweaks

---

## ✅ Checklist: Files Cần Update

Khi update version, PHẢI update **TẤT CẢ** các file sau:

### 1. Core Files (BẮT BUỘC)
- [ ] `MonoStudio_package.json` → `MONO_VERSION`
- [ ] `python/mono_tools/__init__.py` → `__version__`
- [ ] `scripts/startup.py` → print message

### 2. UI Fallback Versions
- [ ] `python/mono_tools/file_manager/file_manager_minibar.py` → fallback `v2.x.x`
- [ ] `python/mono_tools/file_manager/file_manager_settings.py` → fallback `v2.x.x`

### 3. Documentation
- [ ] `instructions.md` → Footer version
- [ ] `docs/Tool_Distribution_Guide.md` → Version line
- [ ] `docs/Simplified_Startup_Guide.md` → Version line
- [ ] `docs/No_Install_Report.md` → Example version

### 4. Test Files (nếu có version)
- [ ] `python/mono_tools/test_demo/test_simplified_startup.py`
- [ ] Các test files khác có print version

### 5. Migration Scripts (nếu có)
- [ ] `python/migration/migrate_all_tools_to_folders.py`

---

## 🔍 Pre-Update Check

Trước khi update version, LUÔN check git tags:

```bash
# Check current tags
git tag --sort=-version:refname

# Check current position
git describe --tags

# Check what changed since last tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

---

## 📝 Update Process

### Step 1: Quyết định version mới
```bash
# Xem tags hiện tại
git tag --sort=-version:refname

# Latest: v2.1.1
# Bạn đang làm: Simplified startup (major refactor)
# → New version: v2.2.0
```

### Step 2: Search & Replace
```bash
# Search tất cả version cũ
grep -r "2\.1\.1" . --include="*.py" --include="*.json" --include="*.md"

# Replace manually hoặc dùng search_replace tool
```

### Step 3: Verify
```bash
# Check all changes
git diff

# Make sure không miss file nào
git status
```

### Step 4: Commit & Tag
```bash
# Stage changes
git add .

# Commit với message rõ ràng
git commit -m "chore: bump version to v2.2.0

- Simplified startup system (200+ → 45 lines)
- Removed auto_load.py (duplicate logic)
- Added Simplified_Startup_Guide.md
- Updated all version references"

# Create git tag
git tag -a v2.2.0 -m "Release v2.2.0: Simplified Startup System"

# Push
git push origin main --tags
```

---

## 🚨 Common Mistakes

### ❌ Version Mismatch
```
Git Tag: v2.1.1
Code: v2.0.0  ← SAI!
```

### ❌ Missing Files
Update 5/10 files → Version không nhất quán

### ❌ Wrong Semantic Version
Bug fix → v2.1.0 instead of v2.0.1

---

## 🎯 Quick Commands

### Check current version everywhere
```bash
# Package JSON
grep MONO_VERSION MonoStudio_package.json

# Python package
grep __version__ python/mono_tools/__init__.py

# Startup script
grep "Mono Studio v" scripts/startup.py

# Git tag
git describe --tags
```

### Find all version references
```bash
# Find all 2.x.x patterns
grep -r "2\.[0-9]\.[0-9]" . --include="*.py" --include="*.json" --include="*.md" | grep -v ".git" | grep -v "__pycache__"
```

---

## 📊 Version History Template

Update README hoặc CHANGELOG:

```markdown
## v2.2.0 (2024-12-19)

### 🎉 New Features
- Simplified startup system (45 lines vs 200+)
- Auto-show MiniBar with 500ms delay

### 🗑️ Removed
- python/startup/auto_load.py (duplicate logic)
- Complex initialize() function

### 📚 Documentation
- Added Simplified_Startup_Guide.md
- Updated all version references

### 📈 Stats
- -161 lines of code
- Faster startup time
- Better maintainability
```

---

## 💡 Pro Tips

1. **Always check git tags first** before updating version
2. **Use semantic versioning** consistently
3. **Update ALL files** at once to avoid mismatch
4. **Commit immediately** after version update
5. **Tag right after commit** for easy tracking
6. **Write clear commit messages** explaining why version bumped

---

## 🔗 Related Commands

```bash
# See all version changes in history
git log --all --grep="version" --oneline

# Compare with previous version
git diff v2.1.1..HEAD

# List all tags with dates
git tag -l --format='%(refname:short) %(creatordate:short)'
```

---

**Last Updated**: 2024-12-19
**Current Version**: v2.2.0

