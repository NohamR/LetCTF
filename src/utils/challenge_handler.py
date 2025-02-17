from ..models import Challenge, File
from typing import List
from pathlib import Path
import requests

def download_files(self, challenge: Challenge, destination: Path) -> List[Path]:
    """Download challenge files to the specified directory"""
    for file in challenge.files:
        file_url = file.url
        name = file.name
        name = name.replace("public.yml", ".yml")
        try:
            response = self.session.get(file_url)
            if response.status_code == 200:
                file_path = destination / name
                file_path.write_bytes(response.content)
                print(f"Downloaded {name} to {destination}")
        except requests.RequestException as e:
            raise f"Error downloading file {file_url}: {e}"