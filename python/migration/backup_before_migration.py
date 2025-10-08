"""
Script backup trước khi migration
"""

import os
import shutil
from datetime import datetime

def create_backup():
    """Tạo backup của cấu trúc hiện tại"""
    print("Creating backup before migration...")
    
    # Tạo tên backup với timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"mono_tools_backup_{timestamp}"
    backup_path = f"backups/{backup_name}"
    
    # Tạo thư mục backup
    os.makedirs(backup_path, exist_ok=True)
    
    # Copy toàn bộ python/mono_tools
    source = "python/mono_tools"
    destination = f"{backup_path}/mono_tools"
    
    if os.path.exists(source):
        shutil.copytree(source, destination)
        print(f"✅ Backup created: {backup_path}")
        print(f"   Source: {source}")
        print(f"   Destination: {destination}")
        return backup_path
    else:
        print(f"❌ Source directory not found: {source}")
        return None

def verify_backup(backup_path):
    """Verify backup được tạo thành công"""
    print(f"\nVerifying backup: {backup_path}")
    
    if not os.path.exists(backup_path):
        print("❌ Backup directory not found")
        return False
    
    # Check key files
    key_files = [
        "mono_tools/__init__.py",
        "mono_tools/qt.py",
        "mono_tools/utils.py",
        "mono_tools/texture_search_replace.py",
        "mono_tools/material_loader.py",
        "mono_tools/file_manager.py"
    ]
    
    missing_files = []
    for file in key_files:
        file_path = os.path.join(backup_path, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing files in backup:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All key files found in backup")
        return True

def main():
    """Main backup function"""
    print("Mono Studio - Pre-Migration Backup")
    print("=" * 40)
    
    try:
        # Create backup
        backup_path = create_backup()
        
        if backup_path:
            # Verify backup
            if verify_backup(backup_path):
                print(f"\n✅ Backup completed successfully!")
                print(f"   Location: {backup_path}")
                print(f"   You can restore from this backup if needed")
            else:
                print(f"\n❌ Backup verification failed!")
                return False
        else:
            print(f"\n❌ Backup creation failed!")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Ready for migration!")
    else:
        print("\n⚠️ Backup failed - do not proceed with migration")
