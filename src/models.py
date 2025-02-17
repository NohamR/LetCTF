from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Challenge:
    id: str
    url: str
    platform: str
    name: str
    author: str
    category: str
    description: str
    difficulty: str
    points: int
    files: List[str]
    additional_info: Dict = None
    template: str = None
    template_translated: str = None
    solved_number: int = 0

@dataclass
class File:
    name: str
    hash: str
    url: str