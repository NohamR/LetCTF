from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Challenge:
    id: str
    url: str
    platform: str
    name: str
    author: str
    category: str
    description: str
    files: List[str]
    difficulty: Optional[int] = None
    points: Optional[int] = None
    additional_info: Dict = None
    template: str = None
    template_translated: str = None
    solved_number: Optional[int] = 0

@dataclass
class File:
    name: str
    url: str
    hash: Optional[str] = None