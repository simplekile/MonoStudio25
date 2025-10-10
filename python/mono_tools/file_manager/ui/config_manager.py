"""
Config Manager
Centralized configuration loading and saving for MonoStudio
"""

import os
import json
from datetime import datetime


class ConfigManager:
    """
    Centralized configuration management
    
    Handles loading/saving all JSON configuration files:
    - department_structure.json
    - asset_type_suggestions.json
    - project metadata (future)
    """
    
    @staticmethod
    def _get_config_dir():
        """Get config directory path"""
        # Config is in mono_tools/file_manager/ directory
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return current_dir
    
    @staticmethod
    def load_department_config():
        """
        Load department structure configuration
        
        Returns:
            dict: Department config or None if error
        """
        try:
            config_dir = ConfigManager._get_config_dir()
            config_path = os.path.join(config_dir, '..', '..', 'config', 'department_structure.json')
            config_path = os.path.normpath(config_path)
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Config file not found: {config_path}")
                return None
        except Exception as e:
            print(f"Error loading department config: {e}")
            return None
    
    @staticmethod
    def save_department_config(config):
        """
        Save department structure configuration
        
        Args:
            config: Configuration dictionary
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            config_dir = ConfigManager._get_config_dir()
            config_path = os.path.join(config_dir, '..', '..', 'config', 'department_structure.json')
            config_path = os.path.normpath(config_path)
            
            # Ensure config directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Update metadata
            config['version'] = config.get('version', '2.0')
            config['last_modified'] = datetime.now().strftime("%Y-%m-%d")
            
            # Save with pretty formatting
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return (True, "Configuration saved successfully")
            
        except Exception as e:
            return (False, f"Failed to save config: {str(e)}")
    
    @staticmethod
    def load_asset_type_suggestions():
        """
        Load asset type autocomplete suggestions
        
        Returns:
            dict: Suggestions dictionary {input: suggestion}
        """
        try:
            config_dir = ConfigManager._get_config_dir()
            suggestions_file = os.path.join(config_dir, 'asset_type_suggestions.json')
            
            if os.path.exists(suggestions_file):
                with open(suggestions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('asset_type_suggestions', {})
            else:
                # Fallback to default suggestions
                return {
                    'char': '_characters',
                    'prop': '_props',
                    'env': '_environments',
                    'veh': '_vehicles',
                    'weap': '_weapons',
                    'fx': '_fx'
                }
        except Exception as e:
            print(f"Error loading asset type suggestions: {e}")
            return {}
    
    @staticmethod
    def load_prefix_mapping():
        """
        Load asset type prefix mapping
        
        Returns:
            dict: Mapping {folder_name: prefix}
        """
        try:
            config_dir = ConfigManager._get_config_dir()
            suggestions_file = os.path.join(config_dir, 'asset_type_suggestions.json')
            
            if os.path.exists(suggestions_file):
                with open(suggestions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('prefix_mapping', {})
            else:
                # Fallback to default mapping
                return {
                    '_characters': 'char_',
                    '_props': 'prop_',
                    '_environments': 'env_',
                    '_vehicles': 'veh_',
                    '_weapons': 'weap_',
                    '_fx': 'fx_'
                }
        except Exception as e:
            print(f"Error loading prefix mapping: {e}")
            return {}
    
    @staticmethod
    def load_display_name_mapping():
        """
        Load asset type display name mapping
        
        Returns:
            dict: Mapping {folder_name: display_name}
        """
        try:
            config_dir = ConfigManager._get_config_dir()
            suggestions_file = os.path.join(config_dir, 'asset_type_suggestions.json')
            
            if os.path.exists(suggestions_file):
                with open(suggestions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('display_name_mapping', {})
            else:
                # Fallback to default mapping
                return {
                    '_characters': 'Character',
                    '_props': 'Prop',
                    '_environments': 'Environment',
                    '_vehicles': 'Vehicle',
                    '_weapons': 'Weapon',
                    '_fx': 'FX'
                }
        except Exception as e:
            print(f"Error loading display name mapping: {e}")
            return {}
    
    @staticmethod
    def load_asset_types():
        """
        Load configured asset types from department config
        
        Returns:
            list: List of asset type dictionaries
        """
        config = ConfigManager.load_department_config()
        if config and 'asset_types' in config:
            return config['asset_types']
        return []
    
    @staticmethod
    def save_asset_type(asset_type_data):
        """
        Add new asset type to configuration
        
        Args:
            asset_type_data: Dictionary with id, name, prefix, etc.
            
        Returns:
            tuple: (success: bool, message: str)
        """
        config = ConfigManager.load_department_config()
        if not config:
            config = {}
        
        if 'asset_types' not in config:
            config['asset_types'] = []
        
        config['asset_types'].append(asset_type_data)
        
        return ConfigManager.save_department_config(config)
    
    @staticmethod
    def update_asset_type(old_id, new_asset_type_data):
        """
        Update existing asset type
        
        Args:
            old_id: Current asset type ID
            new_asset_type_data: New data dictionary
            
        Returns:
            tuple: (success: bool, message: str)
        """
        config = ConfigManager.load_department_config()
        if not config or 'asset_types' not in config:
            return (False, "No asset types found in config")
        
        # Find and update
        found = False
        for i, atype in enumerate(config['asset_types']):
            if atype.get('id') == old_id:
                config['asset_types'][i] = new_asset_type_data
                found = True
                break
        
        if not found:
            return (False, f"Asset type '{old_id}' not found")
        
        return ConfigManager.save_department_config(config)
    
    @staticmethod
    def delete_asset_type(asset_type_id):
        """
        Delete asset type from configuration
        
        Args:
            asset_type_id: Asset type ID to delete
            
        Returns:
            tuple: (success: bool, message: str)
        """
        config = ConfigManager.load_department_config()
        if not config or 'asset_types' not in config:
            return (False, "No asset types found in config")
        
        # Filter out the deleted type
        config['asset_types'] = [
            atype for atype in config['asset_types'] 
            if atype.get('id') != asset_type_id
        ]
        
        return ConfigManager.save_department_config(config)

