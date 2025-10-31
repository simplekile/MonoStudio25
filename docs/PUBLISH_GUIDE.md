# Mono Studio - Publish Guide

## 📋 Tóm Tắt

Đã hoàn thành 3 tasks:
1. ✅ **Kiểm tra version** trong tất cả files
2. ✅ **Tạo script** tự động update version
3. ✅ **Xem diff** trước khi publish

## 🔍 Kết Quả Kiểm Tra Version

### Version Status:
```
[OK] MonoStudio_package.json         -> 2.2.0
[OK] python/mono_tools/__init__.py   -> 2.3.0 ⚠️ MISMATCH
[OK] scripts/startup.py              -> 2.2.0
[OK] file_manager_minibar.py         -> 2.2.0 (line 240)
[OK] file_manager_settings.py        -> 2.2.0 (line 491)
```

### ⚠️ Vấn Đề Phát Hiện:
- **Code version**: 2.3.0 (trong `__init__.py`)
- **Package version**: 2.2.0 (trong `MonoStudio_package.json`)
- **Latest git tag**: v2.2.0
- **Fallback versions**: Còn 2.2.0 (nên update thành 2.3.0)

## 🛠️ Script Tự Động Update Version

**Location**: `python/utilities/update_version.py`

### Usage:
```bash
# Kiểm tra version hiện tại
python python/utilities/update_version.py --check

# Update version (interactive)
python python/utilities/update_version.py 2.3.0

# Dry run (xem sẽ update gì, không thay đổi file)
python python/utilities/update_version.py 2.3.0 --dry-run
```

### Files Script Sẽ Update:
1. `MonoStudio_package.json` → `MONO_VERSION`
2. `python/mono_tools/__init__.py` → `__version__`
3. `scripts/startup.py` → print message
4. `file_manager_minibar.py` → fallback versions (2 places)
5. `file_manager_settings.py` → fallback version

## 📊 Git Status

### Unpushed Commits:
- **55 commits** ahead of origin/main
- **202 files changed**: +35,880 insertions, -1,646 deletions
- **Latest tag**: v2.2.0

### Commits Since Last Tag (v2.2.0):
1. Project Cleanup & Folder Organization Rules
2. Custom styled dialogs (replaces Houdini native)
3. Asset vs Shot department separation
4. UI modularization (reusable components)
5. MiniBar position fixes
6. SmartLineEdit autocomplete
7. Asset Types UI management
8. Subdepartment support
9. New Folder/File features
10. ... và nhiều features khác

## 🚀 Quy Trình Publish

### Option 1: Publish v2.3.0 (Recommended)

Nếu code đã sẵn sàng ở version 2.3.0:

```bash
# 1. Update tất cả versions
python python/utilities/update_version.py 2.3.0

# 2. Review changes
git diff

# 3. Commit version update
git commit -am "chore: bump version to v2.3.0"

# 4. Create git tag
git tag -a v2.3.0 -m "Release v2.3.0: Major improvements

- Custom styled dialogs (ChoiceDialog, InputDialog)
- Asset vs Shot department separation
- UI modularization and reusable components
- SmartLineEdit autocomplete
- Asset Types UI management
- Subdepartment support
- New Folder/File features
- MiniBar position fixes
- Project cleanup and organization"

# 5. Push everything
git push origin main --tags
```

### Option 2: Publish v2.2.0 (Current State)

Nếu muốn giữ tag v2.2.0 và sync code về 2.2.0:

```bash
# 1. Downgrade code version
python python/utilities/update_version.py 2.2.0

# 2. Review và commit
git commit -am "chore: sync version to v2.2.0"

# 3. Push
git push origin main
```

## 📝 Checklist Trước Khi Publish

### Pre-Publish:
- [x] ✅ Kiểm tra version consistency
- [x] ✅ Tạo update script
- [x] ✅ Xem diff và changes
- [ ] ⏳ Test trong Houdini
- [ ] ⏳ Review CHANGELOG
- [ ] ⏳ Update README nếu cần

### Publish Steps:
1. **Update versions** → Dùng script tự động
2. **Commit changes** → Version update commit
3. **Create tag** → Git annotated tag
4. **Push to remote** → `git push origin main --tags`

### Post-Publish:
- [ ] Verify tag trên remote
- [ ] Test package installation
- [ ] Update distribution docs
- [ ] Announce release (nếu cần)

## 📚 Files Đã Tạo

1. **`python/utilities/update_version.py`**
   - Script tự động update version
   - Check version consistency
   - Dry-run mode

2. **`VERSION_REPORT.md`**
   - Báo cáo chi tiết version status
   - Version inconsistency analysis
   - Publish checklist

3. **`PUBLISH_GUIDE.md`** (file này)
   - Hướng dẫn publish đầy đủ
   - Quy trình step-by-step
   - Best practices

## 💡 Recommendations

### Nên publish v2.3.0 vì:
- Code đã ở version 2.3.0
- Có nhiều features mới (55 commits)
- Version mismatch gây confusion

### Nên làm gì:
1. **Chạy dry-run** để xem script sẽ update gì:
   ```bash
   python python/utilities/update_version.py 2.3.0 --dry-run
   ```

2. **Review changes** trước khi commit:
   ```bash
   git diff
   ```

3. **Test trong Houdini** sau khi update version

4. **Push tags** để sync với remote:
   ```bash
   git push origin main --tags
   ```

---

**Next Steps**: 
1. Chạy `python python/utilities/update_version.py 2.3.0 --dry-run` để preview
2. Nếu OK, chạy `python python/utilities/update_version.py 2.3.0` để update
3. Commit và tag như hướng dẫn trên

