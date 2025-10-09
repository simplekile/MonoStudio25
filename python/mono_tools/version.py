"""
Version management for Mono Studio
Tự động lấy version từ git và hiển thị trong UI
"""

import os
import subprocess
import sys
from pathlib import Path

def get_git_version():
    """Lấy version từ git tag hoặc commit hash"""
    try:
        # Tìm git repository root
        current_dir = Path(__file__).parent.parent.parent
        git_dir = current_dir / '.git'
        
        if not git_dir.exists():
            return "dev-unknown"
        
        # Thử lấy latest tag
        try:
            result = subprocess.run(
                ['git', 'describe', '--tags', '--abbrev=0'],
                cwd=current_dir,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
        
        # Nếu không có tag, lấy commit hash
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                cwd=current_dir,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return f"dev-{result.stdout.strip()}"
        except:
            pass
        
        return "dev-unknown"
        
    except Exception as e:
        print(f"⚠️ Error getting git version: {e}")
        return "dev-unknown"

def get_version_info():
    """Lấy thông tin version đầy đủ"""
    try:
        current_dir = Path(__file__).parent.parent.parent
        
        # Git version
        git_version = get_git_version()
        
        # Git branch
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=current_dir,
                capture_output=True,
                text=True,
                timeout=5
            )
            branch = result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            branch = "unknown"
        
        # Git commit date
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%ci'],
                cwd=current_dir,
                capture_output=True,
                text=True,
                timeout=5
            )
            commit_date = result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            commit_date = "unknown"
        
        # Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        return {
            'version': git_version,
            'branch': branch,
            'commit_date': commit_date,
            'python_version': python_version,
            'build_date': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        print(f"⚠️ Error getting version info: {e}")
        return {
            'version': 'dev-unknown',
            'branch': 'unknown',
            'commit_date': 'unknown',
            'python_version': 'unknown',
            'build_date': 'unknown'
        }

# Cache version info
_version_info = None

def get_cached_version_info():
    """Lấy version info với cache"""
    global _version_info
    if _version_info is None:
        _version_info = get_version_info()
    return _version_info

def get_version_string():
    """Lấy version string để hiển thị"""
    info = get_cached_version_info()
    version = info['version']
    # Remove 'v' prefix if it already exists
    if version.startswith('v'):
        version = version[1:]
    return f"v{version} ({info['branch']})"

def get_full_version_string():
    """Lấy full version string"""
    info = get_cached_version_info()
    return f"""Mono Studio {info['version']}
Branch: {info['branch']}
Commit: {info['commit_date']}
Python: {info['python_version']}
Build: {info['build_date']}"""

# Test function
if __name__ == "__main__":
    print("Testing version system...")
    print(f"Version: {get_version_string()}")
    print(f"Full info:")
    print(get_full_version_string())
