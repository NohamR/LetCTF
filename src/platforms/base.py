from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
from http.cookiejar import CookieJar
from pathlib import Path
from ..models import Challenge

class CTFPlatform(ABC):
    """Abstract base class for CTF platforms"""
    def __init__(self, url: str, cookies: Optional[CookieJar] = None):
        self.base_url = url
        self.session = requests.Session()
        if cookies:
            self.session.cookies = cookies

    @abstractmethod
    def login(self, credentials: Dict) -> bool:
        pass

    @abstractmethod
    def get_challenges(self) -> List[Challenge]:
        pass

    @abstractmethod
    def get_challenge(self, challenge_url: str) -> Challenge:
        pass

    @abstractmethod
    def download_challenge_files(self, challenge: Challenge, destination: Path) -> List[Path]:
        pass

    @abstractmethod
    def generate_template(self, challenge: Challenge, hugo_header: bool, translated: bool) -> str:
        pass