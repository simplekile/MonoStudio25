"""
Mono Utilities - Common functions
"""
import os

class MonoUtils:
    """Utility functions for Mono Studio"""
    
    @staticmethod
    def get_studio_path():
        """Get studio root path"""
        return os.environ.get('MONO_STUDIO', '')
    
    @staticmethod
    def get_config_path():
        """Get config directory"""
        return os.environ.get('MONO_CONFIG', '')
    
    @staticmethod
    def log(message):
        """Log message with Mono prefix"""
        print(f"🎬 Mono Studio: {message}")