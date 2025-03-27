import os
import json

def create_file(path: str, default_val: str) -> bool:
    """
    Checks if the file for tracking state of server exists
    """
    if not os.path.exists(path):
        with open(path, 'w') as file:
            file.write(default_val)

def get_file_contents(path: str) -> bool:
    if os.path.exists(path):
        with open(path, 'r') as file:
            value = file.read().strip()
            return value
    return False

def set_file_contents(path: str, value: str) -> bool:
    if os.path.exists(path):
        with open(path, 'w') as file:
            file.write(value)
        return True
    return False


def read_site_config_file(filepath: str) -> dict:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading site config: {e}")
        return {"navBar": []}  # Safe default
