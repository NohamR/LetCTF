import json
from typing import Dict
from pathlib import Path

def load_cookies_from_file(file_path: str | Path) -> Dict:
    """
    Load cookies from a JSON file.
    Expected format:
    {
        "cookie_name1": "cookie_value1",
        "cookie_name2": "cookie_value2"
    }
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Cookie file not found: {file_path}")
    
    with open(path, 'r') as f:
        return json.load(f)