"""
Mono Studio - Cleanup Before Publish Script
Xóa files thừa và organize files trước khi publish
"""

import os
import shutil
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Files to delete
FILES_TO_DELETE = [
    'python/mono_tools/file_manager/file_manager_minibar.py.tmp',
]

# Files to move (from root to docs/)
FILES_TO_MOVE = {
    'PUBLISH_GUIDE.md': 'docs/PUBLISH_GUIDE.md',
    'VERSION_REPORT.md': 'docs/VERSION_REPORT.md',
}

# Folders to check (delete if empty)
FOLDERS_TO_CHECK = [
    'backups',
]


def cleanup():
    """Clean up files before publishing"""
    print("Cleaning up before publish...\n")
    
    deleted = []
    moved = []
    errors = []
    
    # Delete temp files
    print("1. Deleting temporary files...")
    for file_path in FILES_TO_DELETE:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                deleted.append(file_path)
                print(f"   [OK] Deleted: {file_path}")
            except Exception as e:
                errors.append(f"Failed to delete {file_path}: {e}")
                print(f"   [!!] Failed to delete {file_path}: {e}")
        else:
            print(f"   [--] Not found: {file_path}")
    
    # Move files from root to docs/
    print("\n2. Moving files to docs/...")
    for src, dst in FILES_TO_MOVE.items():
        src_path = PROJECT_ROOT / src
        dst_path = PROJECT_ROOT / dst
        
        if src_path.exists():
            if dst_path.exists():
                print(f"   [--] Already exists: {dst}")
            else:
                try:
                    # Ensure docs/ directory exists
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    src_path.rename(dst_path)
                    moved.append(f"{src} -> {dst}")
                    print(f"   [OK] Moved: {src} -> {dst}")
                except Exception as e:
                    errors.append(f"Failed to move {src} to {dst}: {e}")
                    print(f"   [!!] Failed to move {src} -> {dst}: {e}")
        else:
            print(f"   [--] Not found: {src}")
    
    # Check empty folders
    print("\n3. Checking empty folders...")
    for folder in FOLDERS_TO_CHECK:
        folder_path = PROJECT_ROOT / folder
        if folder_path.exists() and folder_path.is_dir():
            try:
                # Check if folder is empty
                if not any(folder_path.iterdir()):
                    folder_path.rmdir()
                    print(f"   [OK] Removed empty folder: {folder}")
                else:
                    print(f"   [--] Folder not empty: {folder}")
            except Exception as e:
                errors.append(f"Failed to remove folder {folder}: {e}")
                print(f"   [!!] Failed to remove {folder}: {e}")
        else:
            print(f"   [--] Folder not found: {folder}")
    
    # Summary
    print("\n" + "="*60)
    print("Summary:")
    print(f"   [OK] Deleted: {len(deleted)} files")
    print(f"   [OK] Moved: {len(moved)} files")
    if errors:
        print(f"   [!!] Errors: {len(errors)}")
    print("="*60)
    
    if deleted:
        print("\nDeleted files:")
        for f in deleted:
            print(f"   - {f}")
    
    if moved:
        print("\nMoved files:")
        for m in moved:
            print(f"   - {m}")
    
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"   - {e}")
    
    print("\n[OK] Cleanup complete!")
    
    return len(deleted) + len(moved), len(errors)


if __name__ == '__main__':
    cleanup()

