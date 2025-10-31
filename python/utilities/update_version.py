"""
Mono Studio - Version Update Script
Tự động update version trong tất cả files cần thiết
"""

import os
import re
import sys
from pathlib import Path

# Get project root (parent of python/)
# Script is in python/utilities/, so go up 2 levels
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Files cần update version
VERSION_FILES = {
    # Core files
    'MonoStudio_package.json': {
        'pattern': r'"MONO_VERSION"\s*:\s*"([^"]+)"',
        'replacement': '"MONO_VERSION" : "{version}"',
        'description': 'Package JSON version'
    },
    'python/mono_tools/__init__.py': {
        'pattern': r'__version__\s*=\s*"([^"]+)"',
        'replacement': '__version__ = "{version}"',
        'description': 'Python package version'
    },
    'scripts/startup.py': {
        'pattern': r'Mono Studio v([\d.]+)',
        'replacement': 'Mono Studio v{version}',
        'description': 'Startup script version'
    },
    # UI fallback versions
    'python/mono_tools/file_manager/file_manager_minibar.py': {
        'pattern': r'version\s*=\s*"([\d.]+)"',
        'replacement': 'version = "{version}"',
        'description': 'MiniBar fallback version (line 2145)',
        'line_range': (2140, 2150)  # Only update around line 2145
    },
    'python/mono_tools/file_manager/file_manager_minibar.py': {
        'pattern': r'"ℹ️ v([\d.]+)"',
        'replacement': '"ℹ️ v{version}"',
        'description': 'MiniBar menu version (line 240)',
        'line_range': (234, 242)  # Only update around line 240
    },
    'python/mono_tools/file_manager/file_manager_settings.py': {
        'pattern': r'QLabel\("v([\d.]+)"\)',
        'replacement': 'QLabel("v{version}")',
        'description': 'Settings fallback version (line 491)',
        'line_range': (489, 493)  # Only update around line 491
    },
}

# Documentation files (optional, có thể skip)
DOC_FILES = [
    'instructions.md',
    'README.md',
    'docs/Tool_Distribution_Guide.md',
    'docs/Simplified_Startup_Guide.md',
    'docs/VERSION_UPDATE_CHECKLIST.md',
]


def find_version_in_file(file_path, pattern):
    """Tìm version trong file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(pattern, content)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"[!!] Error reading {file_path}: {e}")
    return None


def update_file_version(file_path, old_version, new_version, pattern, replacement, line_range=None):
    """Update version trong một file"""
    file_full_path = PROJECT_ROOT / file_path
    
    if not file_full_path.exists():
        print(f"[!!] File not found: {file_path}")
        return False
    
    try:
        with open(file_full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Nếu có line_range, chỉ update trong range đó
        if line_range:
            start_line, end_line = line_range
            # Convert to 0-based index
            start_idx = max(0, start_line - 1)
            end_idx = min(len(lines), end_line)
            
            # Update trong range
            updated = False
            for i in range(start_idx, end_idx):
                line = lines[i]
                if re.search(pattern.replace('([^"]+)', f'({re.escape(old_version)})'), line):
                    new_line = re.sub(
                        pattern.replace('([^"]+)', f'({re.escape(old_version)})'),
                        replacement.format(version=new_version),
                        line
                    )
                    lines[i] = new_line
                    updated = True
                    break
            
            if not updated:
                print(f"   [!!] Pattern not found in range {start_line}-{end_line}")
                return False
        else:
            # Update toàn file
            content = ''.join(lines)
            if old_version not in content:
                print(f"   [!!] Version {old_version} not found in file")
                return False
            
            # Replace version
            new_content = re.sub(
                pattern.replace('([^"]+)', f'({re.escape(old_version)})'),
                replacement.format(version=new_version),
                content
            )
            lines = new_content.splitlines(keepends=True)
        
        # Write back
        with open(file_full_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return True
        
    except Exception as e:
        print(f"   [!!] Error updating {file_path}: {e}")
        return False


def get_current_version():
    """Lấy version hiện tại từ __init__.py"""
    init_file = PROJECT_ROOT / 'python/mono_tools/__init__.py'
    pattern = r'__version__\s*=\s*"([^"]+)"'
    version = find_version_in_file(init_file, pattern)
    return version


def check_all_versions():
    """Kiểm tra version trong tất cả files"""
    # Fix encoding for Windows console
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
    print("Checking versions in all files...\n")
    
    results = {}
    
    # Check core files
    for file_path, config in VERSION_FILES.items():
        full_path = PROJECT_ROOT / file_path
        if not full_path.exists():
            print(f"⚠️ File not found: {file_path}")
            continue
        
        pattern = config['pattern']
        version = find_version_in_file(full_path, pattern)
        
        if version:
            results[file_path] = {
                'version': version,
                'description': config['description']
            }
            print(f"[OK] {file_path:50} -> {version} ({config['description']})")
        else:
            results[file_path] = {
                'version': None,
                'description': config['description']
            }
            print(f"[!!] {file_path:50} -> NOT FOUND ({config['description']})")
    
    return results


def update_all_versions(old_version, new_version, dry_run=False):
    """Update version trong tất cả files"""
    print(f"\nUpdating version: {old_version} -> {new_version}\n")
    
    if dry_run:
        print("DRY RUN MODE - No files will be modified\n")
    
    updated_files = []
    failed_files = []
    
    for file_path, config in VERSION_FILES.items():
        print(f"[*] {file_path}...", end=' ')
        
        if dry_run:
            # Chỉ check xem có update được không
            full_path = PROJECT_ROOT / file_path
            if not full_path.exists():
                print("[!!] NOT FOUND")
                failed_files.append(file_path)
                continue
            
            current_version = find_version_in_file(full_path, config['pattern'])
            if current_version:
                print(f"[OK] Would update: {current_version} -> {new_version}")
            else:
                print("[!!] Pattern not found")
                failed_files.append(file_path)
        else:
            # Thực sự update
            success = update_file_version(
                file_path,
                old_version,
                new_version,
                config['pattern'],
                config['replacement'],
                config.get('line_range')
            )
            
            if success:
                print(f"[OK] Updated")
                updated_files.append(file_path)
            else:
                print(f"[!!] Failed")
                failed_files.append(file_path)
    
    print(f"\nSummary:")
    if not dry_run:
        print(f"   [OK] Updated: {len(updated_files)} files")
    else:
        print(f"   [OK] Would update: {len(updated_files)} files")
    print(f"   [!!] Failed: {len(failed_files)} files")
    
    if failed_files:
        print(f"\n[!!] Failed files:")
        for f in failed_files:
            print(f"   - {f}")
    
    return updated_files, failed_files


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Update Mono Studio version')
    parser.add_argument('new_version', nargs='?', help='New version (e.g., 2.3.0)')
    parser.add_argument('--check', action='store_true', help='Check current versions')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no changes)')
    
    args = parser.parse_args()
    
    if args.check:
        check_all_versions()
        return
    
    if not args.new_version:
        print("[!!] Please provide new version or use --check to see current versions")
        print("\nUsage:")
        print("  python update_version.py --check              # Check current versions")
        print("  python update_version.py 2.3.0                # Update to 2.3.0")
        print("  python update_version.py 2.3.0 --dry-run      # Dry run")
        return
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', args.new_version):
        print(f"[!!] Invalid version format: {args.new_version}")
        print("   Expected format: X.Y.Z (e.g., 2.3.0)")
        return
    
    # Get current version
    current_version = get_current_version()
    if not current_version:
        print("[!!] Cannot determine current version from __init__.py")
        return
    
    print(f"Current version: {current_version}")
    print(f"New version: {args.new_version}\n")
    
    # Confirm
    if not args.dry_run:
        response = input(f"Update version from {current_version} to {args.new_version}? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("[!!] Cancelled")
            return
    
    # Update
    update_all_versions(current_version, args.new_version, dry_run=args.dry_run)
    
    if not args.dry_run:
        print("\n[OK] Version update complete!")
        print("\nNext steps:")
        print(f"   1. Review changes: git diff")
        print(f"   2. Commit: git commit -am 'chore: bump version to v{args.new_version}'")
        print(f"   3. Tag: git tag -a v{args.new_version} -m 'Release v{args.new_version}'")
        print(f"   4. Push: git push origin main --tags")


if __name__ == '__main__':
    main()

