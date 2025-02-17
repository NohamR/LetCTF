from ..models import Challenge, File
from typing import List
from pathlib import Path
import requests
import zipfile
import os

def download_files(self, challenge: Challenge, destination: Path, password: str = None) -> List[Path]:
    """
    Download challenge files to the specified directory and handle zip extraction
    
    Args:
        challenge (Challenge): Challenge object containing files
        destination (Path): Destination directory path
        password (str, optional): Password for encrypted zip files
        
    Returns:
        List[Path]: List of paths to downloaded/extracted files
    """
    
    for file in challenge.files:
        file_url = file.url
        name = file.name
        name = name.replace("public.yml", ".yml")
        
        try:
            response = self.session.get(file_url)
            if response.status_code == 200:
                file_path = destination / name
                file_path.write_bytes(response.content)
                print(f"Downloaded {name} to {file_path}")
                
                # Handle zip files
                if name.lower().endswith('.zip'):
                    try:
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            # Check if zip is password protected
                            if zip_ref.namelist()[0].endswith('/'):
                                is_encrypted = False
                            else:
                                try:
                                    zip_ref.read(zip_ref.namelist()[0])
                                    is_encrypted = False
                                except RuntimeError:
                                    is_encrypted = True
                            
                            # Extract file
                            if is_encrypted and password:
                                zip_ref.extractall(
                                    path=destination,
                                    pwd=password.encode('utf-8')
                                )
                                print(f"Extracted encrypted zip {name} with password")
                            elif not is_encrypted:
                                zip_ref.extractall(path=destination)
                                print(f"Extracted zip {name}")
                            else:
                                print(f"Zip file {name} is encrypted but no password provided")
                            
                            for extracted_file in zip_ref.namelist():
                                extracted_path = destination / extracted_file
                                if extracted_path.is_file():
                                    print(f"Extracted file {extracted_file}")
                    except zipfile.BadZipFile:
                        raise f"Error: {name} is not a valid zip file or password is incorrect"
                
        except requests.RequestException as e:
            raise Exception(f"Error downloading file {file_url}: {e}")