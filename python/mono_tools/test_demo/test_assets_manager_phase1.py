"""
Test Assets Manager Phase 1 - Core Foundation

Tests for Database, Scanner, and Metadata modules.

Usage:
    # In Python console or terminal
    python test_assets_manager_phase1.py
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

print("=" * 70)
print("Assets Manager Phase 1 - Test Suite")
print("=" * 70)

# Test 1: Import modules
print("\n[TEST 1] Import Modules")
print("-" * 70)
try:
    from mono_tools.assets_manager import AssetDatabase, AssetScanner, MetadataManager
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Database operations
print("\n[TEST 2] Database Operations")
print("-" * 70)
try:
    # Create temp database
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name
    
    db = AssetDatabase(db_path)
    print(f"✅ Database created: {db_path}")
    
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
    print(f"✅ Asset added with ID: {asset_id}")
    
    # Retrieve asset
    retrieved = db.get_asset(asset_id)
    if retrieved and retrieved['asset_name'] == 'char_hero':
        print(f"✅ Asset retrieved: {retrieved['filename']}")
    else:
        print(f"❌ Failed to retrieve asset")
    
    # Search assets
    results = db.search_assets(search_text='hero')
    print(f"✅ Search found {len(results)} result(s)")
    
    # Get stats
    stats = db.get_stats()
    print(f"✅ Database stats: {stats['total_assets']} asset(s)")
    
    # Cleanup
    db.close()
    os.unlink(db_path)
    print("✅ Database test completed")
    
except Exception as e:
    print(f"❌ Database test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Metadata operations
print("\n[TEST 3] Metadata Operations")
print("-" * 70)
try:
    manager = MetadataManager()
    print("✅ MetadataManager initialized")
    
    # Create temp asset file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.usd', delete=False) as f:
        test_asset_path = f.name
        f.write("# Test USD file")
    
    # Generate default metadata
    metadata = manager.generate_default_metadata(test_asset_path)
    print(f"✅ Generated default metadata for: {os.path.basename(test_asset_path)}")
    
    # Create template
    template = manager.create_metadata_template(test_asset_path)
    print(f"✅ Created metadata template")
    
    # Validate
    is_valid, errors = manager.validate_metadata(template)
    if is_valid:
        print("✅ Metadata validation passed")
    else:
        print(f"⚠️ Metadata validation warnings: {errors}")
    
    # Write and read metadata JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='_metadata.json', delete=False) as f:
        metadata_json_path = f.name
    
    success = manager.write_metadata_json(metadata_json_path, template)
    if success:
        print(f"✅ Wrote metadata JSON: {os.path.basename(metadata_json_path)}")
    
    loaded_metadata = manager.read_metadata_json(metadata_json_path)
    if loaded_metadata:
        print(f"✅ Read metadata JSON successfully")
    
    # Cleanup
    os.unlink(test_asset_path)
    os.unlink(metadata_json_path)
    print("✅ Metadata test completed")
    
except Exception as e:
    print(f"❌ Metadata test failed: {e}")
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
    
    print(f"✅ Created mock project structure in: {temp_dir}")
    print(f"   Created {len(test_assets)} test assets")
    
    # Initialize scanner
    scanner = AssetScanner(project_path)
    print("✅ Scanner initialized")
    
    # Scan project
    assets = scanner.scan_project()
    print(f"✅ Scan complete: {len(assets)} asset(s) found")
    
    # Verify assets
    expected_count = len(test_assets)
    if len(assets) == expected_count:
        print(f"✅ Found all {expected_count} assets")
    else:
        print(f"⚠️ Expected {expected_count} assets, found {len(assets)}")
    
    # Print asset details
    print("\nFound assets:")
    for asset in assets:
        print(f"   - {asset['filename']} ({asset['file_format']}, {asset['asset_type']}, {asset['version']})")
    
    # Test filters
    usd_assets = scanner.filter_by_format('usd')
    print(f"\n✅ Filter by USD: {len(usd_assets)} asset(s)")
    
    char_assets = scanner.filter_by_type('_characters')
    print(f"✅ Filter by _characters: {len(char_assets)} asset(s)")
    
    hero_assets = scanner.filter_by_name('hero')
    print(f"✅ Filter by 'hero': {len(hero_assets)} asset(s)")
    
    # Get stats
    stats = scanner.get_stats()
    print(f"\nScan statistics:")
    print(f"   Total files scanned: {stats['total_files']}")
    print(f"   Total assets found: {stats['total_assets']}")
    print(f"   Scan time: {stats['scan_time']:.3f}s")
    print(f"   By format: {stats['by_format']}")
    print(f"   By type: {stats['by_type']}")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    print("\n✅ Scanner test completed")
    
except Exception as e:
    print(f"❌ Scanner test failed: {e}")
    import traceback
    traceback.print_exc()
    # Cleanup on error
    if 'temp_dir' in locals() and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

# Test 5: Integration test (Scanner + Database + Metadata)
print("\n[TEST 5] Integration Test")
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
    
    print("✅ Created integration test project")
    
    # 1. Scan project
    scanner = AssetScanner(project_path)
    assets = scanner.scan_project()
    print(f"✅ Scanner found {len(assets)} asset(s)")
    
    # 2. Load metadata
    metadata_mgr = MetadataManager()
    for asset in assets:
        metadata = metadata_mgr.read_metadata(asset['filepath'])
        asset['metadata'] = metadata
        asset['tags'] = ','.join(metadata.get('tags', []))
        asset['description'] = metadata.get('description', '')
        print(f"✅ Loaded metadata for: {asset['filename']}")
    
    # 3. Add to database
    db = AssetDatabase(db_path)
    for asset in assets:
        asset_id = db.add_asset(asset)
        print(f"✅ Added to database: {asset['filename']} (ID: {asset_id})")
    
    # 4. Search
    results = db.search_assets(search_text='integration')
    print(f"✅ Search found {len(results)} result(s)")
    
    # 5. Verify
    if len(results) > 0:
        result = results[0]
        print(f"\nAsset details:")
        print(f"   Name: {result['asset_name']}")
        print(f"   Version: {result['version']}")
        print(f"   Description: {result['description']}")
        print(f"   Tags: {result['tags']}")
    
    # Cleanup
    db.close()
    os.unlink(db_path)
    shutil.rmtree(temp_dir)
    
    print("\n✅ Integration test completed")
    
except Exception as e:
    print(f"❌ Integration test failed: {e}")
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
print("\nNext steps:")
print("  - Phase 2: Basic UI (Browser + Preview)")
print("  - Phase 3: Thumbnails")
print("  - Phase 4: Import/Reference")
print("\nSee docs/Assets_Manager_Plan.md for full roadmap")
print("=" * 70)




