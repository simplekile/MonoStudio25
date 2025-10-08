# Mono Studio - Updated Folder Rules

## 📁 **Folder Classification Guidelines (Updated)**

### 🎯 **Main Package Structure (NEW)**
```
python/
├── mono_tools/                    # Main package (5 tool folders)
│   ├── __init__.py               # Package exports & initialization
│   ├── file_manager/             # File management tool
│   ├── material_loader/          # Material loading tool
│   ├── texture_search_replace/   # Texture search & replace tool
│   ├── qt/                       # Qt/PySide6 utilities
│   ├── utils/                    # General utilities
│   └── test_demo/                # Test & demo scripts
├── analysis/                     # Analysis tools (NEW)
├── migration/                    # Migration tools (NEW)
├── testing/                      # Testing tools (NEW)
├── utilities/                    # Legacy/utility files (NEW)
├── startup/                      # Houdini startup scripts
└── docs/                         # Documentation
```

### 📂 **Folder Naming Conventions (UPDATED)**

#### **Main Package** (`mono_tools/`)
- **Each tool has its own folder**
- **Structure**: `[tool_name]/[tool_name].py` + helpers + integration
- **Example**: `file_manager/file_manager.py`, `texture_search_replace/texture_search_replace.py`

#### **Tool Folders** (`mono_tools/[tool_name]/`)
- `[tool_name].py` - Main tool implementation
- `[tool_name]_menu_integration.py` - Menu/shelf integration
- `[tool_name]_helpers.py` - Helper functions (if needed)
- `[tool_name]_models.py` - Data models (if needed)
- `[tool_name]_api.py` - API wrapper (if needed)
- `__init__.py` - Package exports

#### **Analysis Tools** (`analysis/`) - NEW
- `analyze_[purpose].py` - Analysis scripts
- `simple_[purpose].py` - Simplified analysis scripts
- **Purpose**: Project structure analysis, file categorization

#### **Migration Tools** (`migration/`) - NEW
- `migrate_[purpose].py` - Migration scripts
- `backup_[purpose].py` - Backup scripts
- `test_[purpose].py` - Migration test scripts
- **Purpose**: Project migration, organization, backup

#### **Testing Tools** (`testing/`) - NEW
- `test_[purpose].py` - Test scripts
- `check_[purpose].py` - Consistency check scripts
- `verify_[purpose].py` - Verification scripts
- **Purpose**: Testing, verification, consistency checks

#### **Utilities** (`utilities/`) - NEW
- `[legacy_name].py` - Legacy files
- `[utility_name].py` - Utility scripts
- **Purpose**: Legacy support, utility functions

#### **Test & Demo** (`mono_tools/test_demo/`)
- `test_[feature_name].py` - Unit tests for specific features
- `verify_[feature_name].py` - Verification scripts
- `demo_[feature_name].py` - Demo scripts with examples
- `quick_test_[feature_name].py` - Quick test scripts

#### **Startup** (`startup/`)
- `auto_load.py` - Auto-loading scripts
- `[environment]_startup.py` - Environment-specific startup

#### **Documentation** (`docs/`)
- `[Feature_Name]_Guide.md` - Feature documentation
- `API_Reference.md` - API documentation
- `Troubleshooting.md` - Common issues & solutions

### 🔧 **File Organization Rules (UPDATED)**

#### **1. Tool Files (NEW STRUCTURE)**
```
mono_tools/[tool_name]/
├── __init__.py                           # Package exports
├── [tool_name].py                        # Main tool
├── [tool_name]_menu_integration.py       # Menu integration
├── [tool_name]_helpers.py                # Helper functions (if needed)
├── [tool_name]_models.py                 # Data models (if needed)
└── [tool_name]_api.py                    # API wrapper (if needed)
```

#### **2. Test Files (UNCHANGED)**
```
test_demo/
├── test_[feature_name].py                # Unit tests
├── verify_[feature_name].py              # Verification
├── demo_[feature_name].py                # Demo
└── quick_test_[feature_name].py          # Quick test
```

#### **3. Utility Files (NEW)**
```
analysis/                                 # Analysis tools
├── analyze_[purpose].py
└── simple_[purpose].py

migration/                                # Migration tools
├── migrate_[purpose].py
├── backup_[purpose].py
└── test_[purpose].py

testing/                                  # Testing tools
├── test_[purpose].py
├── check_[purpose].py
└── verify_[purpose].py

utilities/                                # Legacy/utility files
├── [legacy_name].py
└── [utility_name].py
```

#### **4. Documentation Files (UNCHANGED)**
```
docs/
├── [Feature_Name]_Guide.md               # User guide
├── API_Reference.md                      # API docs
└── Troubleshooting.md                    # Common issues
```

### 📋 **File Naming Standards (UPDATED)**

#### **Python Files**
- `snake_case.py` - All Python files
- `[tool_name]/[tool_name].py` - Main tool files
- `[tool_name]/[tool_name]_[type].py` - Tool-related files
- `test_[purpose].py` - Test files
- `demo_[purpose].py` - Demo files
- `verify_[purpose].py` - Verification files
- `analyze_[purpose].py` - Analysis files
- `migrate_[purpose].py` - Migration files

#### **Documentation Files**
- `[Feature_Name]_Guide.md` - User guides
- `[Feature_Name]_API.md` - API documentation
- `[Feature_Name]_Troubleshooting.md` - Troubleshooting guides

#### **Configuration Files**
- `[feature]_config.json` - Configuration files
- `[feature]_settings.py` - Settings modules

### 🗂️ **Folder Creation Rules (UPDATED)**

#### **When to Create New Folders**
1. **Main tools** - Always create `[tool_name]/` folder
2. **Analysis tools** - Use `analysis/` for analysis scripts
3. **Migration tools** - Use `migration/` for migration scripts
4. **Testing tools** - Use `testing/` for testing scripts
5. **Utilities** - Use `utilities/` for legacy/utility files
6. **Test organization** - Always use `test_demo/` for tests
7. **Documentation** - Use `docs/` for all documentation

#### **When NOT to Create Folders**
1. **Single utility files** - Use appropriate utility folder
2. **Small features** - Still create folder for consistency
3. **Over-organization** - Don't create too many nested folders

### 📁 **Example Folder Structure by Feature (UPDATED)**

#### **File Manager Feature (Complex Tool)**
```
python/mono_tools/file_manager/
├── __init__.py
├── file_manager.py                     # Main tool
├── file_manager_api.py                 # API wrapper
├── file_manager_helpers.py             # Helper functions
├── file_manager_manager.py             # Manager class
├── file_manager_minibar.py             # MiniBar component
├── file_manager_models.py              # Data models
└── file_manager_menu_integration.py    # Menu integration

python/mono_tools/test_demo/
├── test_file_manager.py                # Unit tests
└── demo_file_manager.py                # Demo

docs/
└── File_Manager_Guide.md               # Documentation
```

#### **Texture Search & Replace Feature (Simple Tool)**
```
python/mono_tools/texture_search_replace/
├── __init__.py
├── texture_search_replace.py           # Main tool
└── texture_menu_integration.py         # Menu integration

python/mono_tools/test_demo/
├── test_texture_search_replace.py      # Unit tests
└── demo_texture_search_replace.py      # Demo

docs/
└── Texture_Search_Replace_Guide.md     # Documentation
```

#### **Analysis Tools (NEW)**
```
python/analysis/
├── __init__.py
├── analyze_current_structure.py        # Structure analysis
├── analyze_tool_structure.py           # Tool analysis
├── analyze_remaining_files.py          # File analysis
└── simple_analyze.py                   # Simple analysis
```

#### **Migration Tools (NEW)**
```
python/migration/
├── __init__.py
├── migrate_all_tools_to_folders.py     # Migration script
├── backup_before_migration.py          # Backup script
└── simple_migration_test.py            # Migration test
```

### 🎯 **Best Practices (UPDATED)**

#### **1. Keep Related Files Together**
- All tool files in `[tool_name]/` folder
- All tests in `test_demo/`
- All docs in `docs/`
- All utilities in appropriate utility folders

#### **2. Use Descriptive Names**
- `texture_search_replace.py` not `texture.py`
- `test_texture_search_replace.py` not `test.py`
- `Texture_Search_Replace_Guide.md` not `guide.md`

#### **3. Maintain Consistency**
- Same naming pattern across all features
- Same folder structure for similar features
- Same file organization principles
- All tools have folders (no exceptions)

#### **4. Tool Distribution**
- Follow 4-level access pattern (File → Package → Menu → Shelf)
- Each tool has consistent access methods
- Maintain separation between core tools and utilities

#### **5. Tool Consistency**
- Follow naming conventions: `[tool_name].py`, `show_[tool_name]()`
- All tools must have menu integration
- All tools must have shelf integration
- All tools must have Python API
- All tools must have documentation

### 🚀 **Deployment Checklist (UPDATED)**

- [ ] All imports use PySide6
- [ ] Relative imports for internal modules
- [ ] Error handling for Houdini environment
- [ ] **Folder structure follows guidelines**
- [ ] **Files named according to conventions**
- [ ] **Function naming follows conventions**
- [ ] **Menu integration implemented**
- [ ] **Shelf integration implemented**
- [ ] **All tools have dedicated folders**
- [ ] Test files in `test_demo/` folder
- [ ] Documentation in `docs/` folder
- [ ] Utility files in appropriate folders
- [ ] Added to `__init__.py` exports
- [ ] **Consistency check passes**
- [ ] Documentation updated
- [ ] Tested in Houdini 21+

### 🔍 **Common Issues & Solutions (UPDATED)**

#### Issue: Tool files scattered in root
**Solution**: Create `[tool_name]/` folder and move all related files

#### Issue: Utility files mixed with main tools
**Solution**: Move to appropriate utility folder (`analysis/`, `migration/`, `testing/`, `utilities/`)

#### Issue: Inconsistent folder structure
**Solution**: Follow the updated folder classification guidelines

#### Issue: Missing menu integration
**Solution**: Create `[tool_name]_menu_integration.py` in tool folder

---

**Updated**: October 8, 2025
**Status**: Applied to current project structure
**Next Review**: When adding new tools or features
