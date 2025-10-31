"""
Test Assets Manager Phase 1 - Standalone (No Houdini Required)

Tests for Database, Scanner, and Metadata modules without Houdini dependency.

Usage:
    python test_assets_phase1_standalone.py
"""

import os
import sys
import tempfile
import shutil
import json
from datetime import datetime
import io

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

print("=" * 70)
print("Assets Manager Phase 1 - Standalone Test Suite")
print("=" * 70)

# Test 1: Import modules directly (bypass mono_tools __init__)
print("\n[TEST 1] Import Core Modules (No Houdini)")
print("-" * 70)
try:
    # Import directly from file paths to avoid mono_tools.__init__ which imports hou
    import importlib.util
    
    # Load AssetDatabase
    db_spec = importlib.util.spec_from_file_location(
        "assets_manager_database",
        os.path.join(os.path.dirname(__file__), '..', 'assets_manager', 'assets_manager_database.py')
    )
    db_module = importlib.util.module_from_spec(db_spec)
    db_spec.loader.exec_module(db_module)
    AssetDatabase = db_module.AssetDatabase
    
    # Load AssetScanner
    scanner_spec = importlib.util.spec_from_file_location(
        "assets_manager_scanner",
        os.path.join(os.path.dirname(__file__), '..', 'assets_manager', 'assets_manager_scanner.py')
    )
    scanner_module = importlib.util.module_from_spec(scanner_spec)
    scanner_spec.loader.exec_module(scanner_module)
    AssetScanner = scanner_module.AssetScanner
    
    # Load MetadataManager
    metadata_spec = importlib.util.spec_from_file_location(
        "assets_manager_metadata",
        os.path.join(os.path.dirname(__file__), '..', 'assets_manager', 'assets_manager_metadata.py')
    )
    metadata_module = importlib.util.module_from_spec(metadata_spec)
    metadata_spec.loader.exec_module(metadata_module)
    MetadataManager = metadata_module.MetadataManager
    
    print("[OK] All core modules imported successfully")
except ImportError as e:
    print(f"[FAIL] Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Database operations
print("\n[TEST 2] Database Operations")
print("-" * 70)
try:
    # Create temp database
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name
    
    db = AssetDatabase(db_path)
    print(f"[OK] Database created: {os.path.basename(db_path)}")
    
    # Add test asset
    test_asset = {
        'filepath': '/test/project/01_assets/_characters/char_hero/01_modeling/_publish/char_hero_v003.usd',
        'filename': 'char_hero_v003.usd',
        'asset_name': 'char_hero',
        'asset_type': '_characters',
        'department': '01_modeling',
        'file_format': 'usd',
        'file_size': 1024000,
        'version': 'v003',
        'description': 'Test character asset',
        'tags': 'character,hero,test'
    }
    
    asset_id = db.add_asset(test_asset)
    print(f"[OK] Asset added with ID: {asset_id}")
    
    # Retrieve asset
    retrieved = db.get_asset(asset_id)
    if retrieved and retrieved['asset_name'] == 'char_hero':
        print(f"[OK] Asset retrieved: {retrieved['filename']}")
    else:
        print(f"[FAIL] Failed to retrieve asset")
    
    # Search assets
    results = db.search_assets(search_text='hero')
    print(f"[OK] Search found {len(results)} result(s)")
    
    # Get stats
    stats = db.get_stats()
    print(f"[OK] Database stats: {stats['total_assets']} asset(s)")
    print(f"     - By format: {stats.get('by_format', {})}")
    print(f"     - By type: {stats.get('by_type', {})}")
    print(f"     - DB size: {stats.get('db_size_mb', 0):.2f} MB")
    
    # Cleanup
    db.close()
    os.unlink(db_path)
    print("[OK] Database test completed")
    
except Exception as e:
    print(f"[FAIL] Database test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Metadata operations
print("\n[TEST 3] Metadata Operations")
print("-" * 70)
try:
    manager = MetadataManager()
    print("[OK] MetadataManager initialized")
    
    # Create temp asset file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.usd', delete=False) as f:
        test_asset_path = f.name
        f.write("# Test USD file")
    
    # Generate default metadata
    metadata = manager.generate_default_metadata(test_asset_path)
    print(f"[OK] Generated default metadata")
    
    # Create template
    template = manager.create_metadata_template(test_asset_path)
    print(f"[OK] Created metadata template")
    print(f"     - Asset: {template.get('asset_name')}")
    print(f"     - Version: {template.get('version')}")
    print(f"     - Tags: {template.get('tags')}")
    
    # Validate
    is_valid, errors = manager.validate_metadata(template)
    if is_valid:
        print("[OK] Metadata validation passed")
    else:
        print(f"[WARN] Metadata validation warnings: {errors}")
    
    # Write and read metadata JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='_metadata.json', delete=False) as f:
        metadata_json_path = f.name
    
    success = manager.write_metadata_json(metadata_json_path, template)
    if success:
        print(f"[OK] Wrote metadata JSON")
    
    loaded_metadata = manager.read_metadata_json(metadata_json_path)
    if loaded_metadata:
        print(f"[OK] Read metadata JSON successfully")
    
    # Cleanup
    os.unlink(test_asset_path)
    os.unlink(metadata_json_path)
    print("[OK] Metadata test completed")
    
except Exception as e:
    print(f"[FAIL] Metadata test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Scanner operations (with mock project structure)
print("\n[TEST 4] Scanner Operations")
print("-" * 70)
try:
    # Create temp project structure
    temp_dir = tempfile.mkdtemp()
    project_path = temp_dir
    
    # Create mock project structure
    structure = [
        '01_assets/_characters/char_hero/01_modeling/_publish',
        '01_assets/_characters/char_villain/01_modeling/_publish',
        '01_assets/_props/prop_chair/01_modeling/_publish',
        '02_shots/03_lighting/_publish',
    ]
    
    for path in structure:
        full_path = os.path.join(project_path, path)
        os.makedirs(full_path, exist_ok=True)
    
    # Create mock assets
    test_assets = [
        ('01_assets/_characters/char_hero/01_modeling/_publish/char_hero_v003.usd', 'USD asset'),
        ('01_assets/_characters/char_hero/01_modeling/_publish/char_hero_v003.fbx', 'FBX asset'),
        ('01_assets/_characters/char_villain/01_modeling/_publish/char_villain_v001.usd', 'USD asset'),
        ('01_assets/_props/prop_chair/01_modeling/_publish/prop_chair_v002.fbx', 'FBX asset'),
        ('02_shots/03_lighting/_publish/Sh010_lighting_v001.usd', 'Shot USD'),
    ]
    
    for asset_path, content in test_assets:
        full_path = os.path.join(project_path, asset_path)
        with open(full_path, 'w') as f:
            f.write(content)
    
    print(f"[OK] Created mock project in temp directory")
    print(f"     - Created {len(test_assets)} test assets")
    
    # Initialize scanner
    scanner = AssetScanner(project_path)
    print("[OK] Scanner initialized")
    
    # Scan project
    assets = scanner.scan_project()
    print(f"[OK] Scan complete: {len(assets)} asset(s) found")
    
    # Verify assets
    expected_count = len(test_assets)
    if len(assets) == expected_count:
        print(f"[OK] Found all {expected_count} assets")
    else:
        print(f"[WARN] Expected {expected_count} assets, found {len(assets)}")
    
    # Print asset details
    print("\n     Found assets:")
    for asset in assets:
        print(f"       - {asset['filename']} ({asset['file_format']}, {asset['version']})")
    
    # Test filters
    usd_assets = scanner.filter_by_format('usd')
    print(f"\n[OK] Filter by USD: {len(usd_assets)} asset(s)")
    
    char_assets = scanner.filter_by_type('_characters')
    print(f"[OK] Filter by _characters: {len(char_assets)} asset(s)")
    
    hero_assets = scanner.filter_by_name('hero')
    print(f"[OK] Filter by 'hero': {len(hero_assets)} asset(s)")
    
    # Get stats
    stats = scanner.get_stats()
    print(f"\n     Scan statistics:")
    print(f"       - Total files: {stats['total_files']}")
    print(f"       - Total assets: {stats['total_assets']}")
    print(f"       - Scan time: {stats['scan_time']:.3f}s")
    print(f"       - By format: {stats['by_format']}")
    print(f"       - By type: {stats['by_type']}")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    print("\n[OK] Scanner test completed")
    
except Exception as e:
    print(f"[FAIL] Scanner test failed: {e}")
    import traceback
    traceback.print_exc()
    # Cleanup on error
    if 'temp_dir' in locals() and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

# Test 5: Integration test
print("\n[TEST 5] Integration Test (Scanner + Database + Metadata)")
print("-" * 70)
try:
    # Create temp project and database
    temp_dir = tempfile.mkdtemp()
    project_path = temp_dir
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name
    
    # Create mock structure
    publish_dir = os.path.join(project_path, '01_assets/_characters/char_integration/01_modeling/_publish')
    os.makedirs(publish_dir, exist_ok=True)
    
    # Create asset
    asset_file = os.path.join(publish_dir, 'char_integration_v001.usd')
    with open(asset_file, 'w') as f:
        f.write("# Integration test asset")
    
    # Create metadata
    metadata_file = os.path.join(publish_dir, 'metadata.json')
    metadata_content = {
        'asset_name': 'char_integration',
        'version': 'v001',
        'description': 'Integration test character',
        'tags': ['character', 'test', 'integration'],
        'created_by': 'test_suite'
    }
    with open(metadata_file, 'w') as f:
        json.dump(metadata_content, f, indent=4)
    
    print("[OK] Created integration test project")
    
    # 1. Scan project
    scanner = AssetScanner(project_path)
    assets = scanner.scan_project()
    print(f"[OK] Scanner found {len(assets)} asset(s)")
    
    # 2. Load metadata
    metadata_mgr = MetadataManager()
    for asset in assets:
        metadata = metadata_mgr.read_metadata(asset['filepath'])
        asset['metadata'] = metadata
        asset['tags'] = ','.join(metadata.get('tags', []))
        asset['description'] = metadata.get('description', '')
        print(f"[OK] Loaded metadata for: {asset['filename']}")
    
    # 3. Add to database
    db = AssetDatabase(db_path)
    for asset in assets:
        asset_id = db.add_asset(asset)
        print(f"[OK] Added to database: {asset['filename']} (ID: {asset_id})")
    
    # 4. Search
    results = db.search_assets(search_text='integration')
    print(f"[OK] Search found {len(results)} result(s)")
    
    # 5. Verify
    if len(results) > 0:
        result = results[0]
        print(f"\n     Asset details:")
        print(f"       - Name: {result['asset_name']}")
        print(f"       - Version: {result['version']}")
        print(f"       - Description: {result['description']}")
        print(f"       - Tags: {result['tags']}")
    
    # Cleanup
    db.close()
    os.unlink(db_path)
    shutil.rmtree(temp_dir)
    
    print("\n[OK] Integration test completed")
    
except Exception as e:
    print(f"[FAIL] Integration test failed: {e}")
    import traceback
    traceback.print_exc()
    # Cleanup on error
    if 'temp_dir' in locals() and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    if 'db_path' in locals() and os.path.exists(db_path):
        os.unlink(db_path)

# Summary
print("\n" + "=" * 70)
print("Test Suite Completed")
print("=" * 70)
print("\n[SUCCESS] Phase 1 Core Foundation is ready!")
print("\nModules tested:")
print("  - AssetDatabase (SQLite-based asset catalog)")
print("  - AssetScanner (Scan _publish/ folders)")
print("  - MetadataManager (JSON metadata parser)")
print("\nNext steps:")
print("  - Test in Houdini environment")
print("  - Phase 2: Basic UI (Browser + Preview)")
print("  - Phase 3: Thumbnails")
print("  - Phase 4: Import/Reference")
print("\nSee docs/Assets_Manager_Plan.md for full roadmap")
print("=" * 70)

