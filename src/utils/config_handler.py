import json
from typing import Dict
from pathlib import Path

def load_config(file_path: str | Path) -> Dict:
    """Load configuration from a JSON file
    Expected format:
    {
        "token": "your_token",
        "provider": "provider_name"
    }
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {file_path}")
    
    with open(path, 'r') as f:
        return json.load(f)