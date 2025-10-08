"""
Test and Demo modules for Mono Studio
Chứa các script test và demo cho các tính năng của Mono Studio
"""

# Test functions
from .test_pyside6 import run_all_tests as test_pyside6
from .verify_pyside6 import run_verification as verify_pyside6
from .test_texture_search_replace import run_all_tests as test_texture_search_replace
from .test_menu_shelf import test_all_access_methods as test_menu_shelf

# Demo functions
from .demo_texture_search_replace import run_full_demo as demo_texture_search_replace

# Quick test
from .quick_test_pyside6 import quick_test, test_texture_tool

__all__ = [
    'test_pyside6',
    'verify_pyside6', 
    'test_texture_search_replace',
    'test_menu_shelf',
    'demo_texture_search_replace',
    'quick_test',
    'test_texture_tool'
]
