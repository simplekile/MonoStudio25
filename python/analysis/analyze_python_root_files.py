"""
Analyze files in python/ root folder
"""

import os

def analyze_python_root_files():
    """Analyze files in python/ root folder"""
    print("Analyzing files in python/ root folder...")
    
    python_path = "python"
    
    # Get all files in python root
    root_files = []
    for filename in os.listdir(python_path):
        if filename.endswith('.py') and not filename.startswith('__'):
            root_files.append(filename)
    
    print(f"Found {len(root_files)} files in python/ root:")
    for file in root_files:
        print(f"  - {file}")
    
    # Categorize files
    analysis_files = []
    migration_files = []
    test_files = []
    utility_files = []
    core_files = []
    unknown_files = []
    
    for file in root_files:
        if file.startswith('analyze_') or file.startswith('simple_analyze') or file.startswith('simple_structure'):
            analysis_files.append(file)
        elif file.startswith('migrate_') or file.startswith('backup_') or file.startswith('simple_migration'):
            migration_files.append(file)
        elif file.startswith('test_') or file.startswith('check_') or file.startswith('simple_consistency'):
            test_files.append(file)
        elif file.startswith('mono_') or file.startswith('Mono_'):
            core_files.append(file)
        elif file in ['123.py']:
            utility_files.append(file)
        else:
            unknown_files.append(file)
    
    print(f"\nCategorization:")
    print(f"  Analysis files: {len(analysis_files)}")
    for file in analysis_files:
        print(f"    - {file}")
    
    print(f"  Migration files: {len(migration_files)}")
    for file in migration_files:
        print(f"    - {file}")
    
    print(f"  Test files: {len(test_files)}")
    for file in test_files:
        print(f"    - {file}")
    
    print(f"  Core files: {len(core_files)}")
    for file in core_files:
        print(f"    - {file}")
    
    print(f"  Utility files: {len(utility_files)}")
    for file in utility_files:
        print(f"    - {file}")
    
    print(f"  Unknown files: {len(unknown_files)}")
    for file in unknown_files:
        print(f"    - {file}")
    
    return analysis_files, migration_files, test_files, core_files, utility_files, unknown_files

def recommend_organization(analysis_files, migration_files, test_files, core_files, utility_files, unknown_files):
    """Recommend organization for root files"""
    print(f"\nOrganization Recommendations:")
    print("-" * 40)
    
    print("1. CREATE UTILITY FOLDERS:")
    print("   mkdir python/analysis/")
    print("   mkdir python/migration/")
    print("   mkdir python/testing/")
    print("   mkdir python/utilities/")
    
    if analysis_files:
        print(f"\n2. MOVE ANALYSIS FILES to analysis/:")
        for file in analysis_files:
            print(f"   move {file} -> analysis/")
    
    if migration_files:
        print(f"\n3. MOVE MIGRATION FILES to migration/:")
        for file in migration_files:
            print(f"   move {file} -> migration/")
    
    if test_files:
        print(f"\n4. MOVE TEST FILES to testing/:")
        for file in test_files:
            print(f"   move {file} -> testing/")
    
    if utility_files:
        print(f"\n5. MOVE UTILITY FILES to utilities/:")
        for file in utility_files:
            print(f"   move {file} -> utilities/")
    
    if core_files:
        print(f"\n6. CORE FILES - Keep in root or move to appropriate location:")
        for file in core_files:
            print(f"   - {file} (need to determine best location)")
    
    if unknown_files:
        print(f"\n7. UNKNOWN FILES - Need analysis:")
        for file in unknown_files:
            print(f"   - {file} (need to determine category)")

def main():
    """Main analysis function"""
    print("Mono Studio - Python Root Files Analysis")
    print("=" * 50)
    
    try:
        analysis_files, migration_files, test_files, core_files, utility_files, unknown_files = analyze_python_root_files()
        recommend_organization(analysis_files, migration_files, test_files, core_files, utility_files, unknown_files)
        
        total_files = len(analysis_files) + len(migration_files) + len(test_files) + len(core_files) + len(utility_files) + len(unknown_files)
        
        print(f"\nSummary:")
        print(f"  Total files in python/ root: {total_files}")
        print(f"  Analysis files: {len(analysis_files)}")
        print(f"  Migration files: {len(migration_files)}")
        print(f"  Test files: {len(test_files)}")
        print(f"  Core files: {len(core_files)}")
        print(f"  Utility files: {len(utility_files)}")
        print(f"  Unknown files: {len(unknown_files)}")
        
        if total_files > 0:
            print(f"\nACTION NEEDED: {total_files} files in python/ root need organization")
            print("Recommendation: Create utility folders and organize files by category")
        else:
            print("\nSUCCESS: All files are properly organized!")
        
    except Exception as e:
        print(f"ERROR: Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
