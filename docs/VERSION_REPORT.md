# Mono Studio - Version Status Report

Generated: 2025-01-XX

## Quick Summary

**Current Status:**
- Code version: **2.3.0** (in `__init__.py`)
- Package version: **2.2.0** (in `MonoStudio_package.json`) ⚠️
- Latest git tag: **v2.2.0**
- Unpushed commits: **55 commits** ahead of origin/main

**Action Needed:**
- Sync all versions to **2.3.0** OR create new tag **v2.3.0**
- Or downgrade code to 2.2.0 if 2.3.0 is not ready

## 📊 Current Version Status

### Git Tags
- Latest tag: v2.2.0
- Current position: v2.2.0-50-g8fb4386 (50 commits ahead)
- All tags: v2.2.0, v2.1.1, v2.1.0

### Code Versions

#### ✅ Core Files (CURRENT)
| File | Version | Status |
|------|---------|--------|
| `python/mono_tools/__init__.py` | 2.3.0 | ✅ Latest |
| `MonoStudio_package.json` | 2.2.0 | ⚠️ Outdated |
| `scripts/startup.py` | v2.2.0 | ⚠️ Outdated |

#### ⚠️ UI Fallback Versions
| File | Location | Version | Status |
|------|----------|---------|--------|
| `file_manager_minibar.py` | Line 240 | 2.2.0 | ⚠️ Outdated |
| `file_manager_minibar.py` | Line 2145 | 2.3.0 | ✅ Latest |
| `file_manager_settings.py` | Line 491 | 2.2.0 | ⚠️ Outdated |

#### 📚 Documentation Versions
| File | Version References | Status |
|------|-------------------|--------|
| `README.md` | v2.0.0 | ⚠️ Outdated |
| `instructions.md` | v2.0.0, v2.2.0 | ⚠️ Mixed |
| `docs/INDEX.md` | v2.2.0 | ⚠️ Outdated |
| `docs/Tool_Distribution_Guide.md` | 2.2.0 | ⚠️ Outdated |

## 🎯 Version Consistency Issues

### Issues Found:
1. **Package JSON** has 2.2.0 but code has 2.3.0
2. **Startup script** prints v2.2.0 but should print v2.3.0
3. **Fallback versions** are inconsistent (some 2.2.0, some 2.3.0)
4. **Documentation** references old versions (v2.0.0, v2.2.0)

### Recommended Action:
- Decide on target version (likely 2.3.0 to match code)
- Update all files to consistent version
- Create git tag v2.3.0
- Push to remote

## 📝 Recent Changes (Unpushed Commits)

Last 10 commits ahead of origin/main:
1. 8fb4386 - 📝 Added detailed commit notes for 4b0e72a
2. 4b0e72a - ✨ Project Cleanup & Folder Organization Rules
3. ad9f92d - fix: ChoiceDialog lambda syntax error
4. 70d75b6 - feat: replace native Houdini dialogs with custom MonoStudio styled dialogs
5. 8df6969 - feat: separate Asset vs Shot department configs
6. 3d64840 - refactor: modularize UI components for reusability
7. 7b0f432 - fix: add missing _load_display_name_mapping method
8. 7bc3714 - fix: delay MiniBar position restore on startup
9. 6de59fb - fix: remove ALL screen position constraints from MiniBar
10. c0cfb51 - fix: MiniBar position restore - allow right edge to extend beyond screen

## 🚀 Publish Checklist

### Before Publishing:
- [ ] Run version check script: `python python/utilities/update_version.py --check`
- [ ] Update all versions to consistent value
- [ ] Review all changes: `git diff`
- [ ] Test in Houdini
- [ ] Update CHANGELOG/README if needed

### Publishing Steps:
1. **Update Version**: `python python/utilities/update_version.py 2.3.0`
2. **Commit**: `git commit -am "chore: bump version to v2.3.0"`
3. **Tag**: `git tag -a v2.3.0 -m "Release v2.3.0: [Description]"`
4. **Push**: `git push origin main --tags`

### After Publishing:
- [ ] Verify tag exists on remote: `git ls-remote --tags origin`
- [ ] Create GitHub release (if applicable)
- [ ] Update distribution docs if needed

---

**Script Created**: `python/utilities/update_version.py`
**Usage**: 
- Check: `python python/utilities/update_version.py --check`
- Update: `python python/utilities/update_version.py 2.3.0`
- Dry run: `python python/utilities/update_version.py 2.3.0 --dry-run`

