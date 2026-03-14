"""
Environment variable loader for AutoResearch Bio-Medical Pipeline
"""

import os
from pathlib import Path

def load_env_variables():
    """
    Load environment variables from .env files
    Looks for .env files in the current directory and parent directories
    """
    # Look for .env files in the current directory and parent directories
    current_dir = Path.cwd()
    
    # Check for various .env file names
    env_files = [
        '.env.local',      # Local overrides
        '.env',           # Main environment file
        '.env.example',   # Example file (should not contain actual secrets)
    ]
    
    # Search in current directory and parent directories up to 3 levels up
    for _ in range(4):
        for env_file in env_files:
            env_path = current_dir / env_file
            if env_path.exists():
                try:
                    # Load the .env file
                    with open(env_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip()
                                
                                # Remove quotes if present
                                if (value.startswith('"') and value.endswith('"')) or \
                                   (value.startswith("'") and value.endswith("'")):
                                    value = value[1:-1]
                                
                                # Only set if not already set
                                if not os.getenv(key):
                                    os.environ[key] = value
                except Exception as e:
                    print(f"Warning: Could not load {env_path}: {e}")
        
        # Move up one directory level
        if current_dir.parent == current_dir:
            break
        current_dir = current_dir.parent

# Also try to load using python-dotenv if available
def load_env_with_dotenv():
    """
    Load environment variables using python-dotenv if available
    """
    try:
        from dotenv import load_dotenv
        # Try loading from various locations
        load_dotenv('.env.local', override=False)
        load_dotenv('.env', override=False)
        load_dotenv('.env.example', override=False)
        
        # Also try to load from parent directories
        import pathlib
        for env_file in ['.env.local', '.env', '.env.example']:
            # Walk up the directory tree
            current_path = pathlib.Path.cwd()
            for _ in range(5):  # Go up max 5 levels
                env_path = current_path / env_file
                if env_path.exists():
                    load_dotenv(env_path, override=False)
                    break
                if current_path.parent == current_path:
                    break
                current_path = current_path.parent
    except ImportError:
        # python-dotenv not available, fall back to manual loading
        pass
    except Exception as e:
        print(f"Warning: Could not load .env with python-dotenv: {e}")

# Load environment variables when this module is imported
load_env_with_dotenv()
load_env_variables()