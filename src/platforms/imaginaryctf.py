from typing import List, Dict
from pathlib import Path
from .base import CTFPlatform
from ..models import Challenge, File
from ..utils.config_handler import load_config
from ..utils.challenge_handler import download_files
from bs4 import BeautifulSoup
from datetime import datetime
import textwrap
import requests
import re

class ImaginaryCTFPlatform(CTFPlatform):
    def __init__(self, url: str = "https://imaginaryctf.org/"):
        super().__init__(url)
        self.url = url
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
    def login(self) -> bool:
        """Not implementing login since we don't need it :D"""
        return True
    
    def get_challenges(self) -> List[Challenge]:
        """Get all challenges from platform"""
        try:
            response = self.session.get('https://imaginaryctf.org/Challenges', headers=self.headers)
            if response.status_code != 200:
                raise Exception(f"Error fetching challenges: {response.status_code}")
        except requests.RequestException as e:
            raise Exception(f"Error fetching challenges: {e}")
        
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, 'html.parser')
        challenges = {}
        
        for category_header in soup.find_all('h3', class_='text-start'):
            category = category_header.text.strip()
            
            current_element = category_header.find_next('div', class_='card challenge')
            
            while current_element and not current_element.find_parent('h3'):
                header = current_element.find('div', class_='challenge-header')
                if not header:
                    continue
                    
                header_text = header.text.strip()
                name = header_text.split('(')[0].strip()
                points = int(header_text.split('(')[1].split('pts')[0].strip())
                
                modal_id = current_element.find('a')['data-bs-target'].replace('#', '')
                modal = soup.find('div', id=modal_id)
                
                if modal:
                    modal_title = modal.find('h5', class_='modal-title')
                    author = modal_title.find('small', class_='text-muted').text.replace('by', '').strip()
                    solve_count = int(modal_title.find('span').text.split('solves')[0].strip('- '))
                    
                    description = modal.find('p').text.strip()
                    
                    files = []
                    attachments_section = modal.find('b', text='Attachments')
                    if attachments_section:
                        files = [a['href'] for a in attachments_section.find_next('p').find_all('a')]
                    
                    challenge_id = name.lower().replace(' ', '-')
                    
                    challenge = Challenge(
                        id=challenge_id,
                        url='https://imaginaryctf.org/Challenges',
                        platform="ImaginaryCTF",
                        name=name,
                        author=author,
                        category=category,
                        description=description,
                        points=points,
                        files=files,
                        solved_number=solve_count
                    )
                    
                    challenges[challenge_id] = challenge
                
                current_element = current_element.find_next('div', class_='card challenge')
        
        self.challenges = challenges

    def resolve_challenge_files(self, file_url: Challenge):
        """Resolve file URL to get direct download link it"""
        print(f"Resolving file URL: {file_url}")
        api_url = "https://cybersharing.net/api/containers/" + file_url.split('/')[-1]
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://cybersharing.net',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        data = {"password":None}
        response = self.session.post(api_url, headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"Error fetching file: {response.status_code}")
        response = response.json()
        folder_id = response['id']
        signature = response['signature']
        files = []
        for upload in response['uploads']:
            name = upload['fileName']
            file_url = f"https://cybersharing.net/api/download/file/{folder_id}/{upload['id']}/{signature}/{name}"
            hash = None
            file = File(name=name, url=file_url, hash=hash)
            files.append(file)
        
        return files
    
    def get_challenge(self, challenge_url: str) -> Challenge:
        """Get a specific challenge by URL"""
        
        challenge = self.challenges.get(challenge_url)
        not_resolved_files = challenge.files
        allfiles = []
        for file_url in not_resolved_files:
            files = self.resolve_challenge_files(file_url)
            allfiles = allfiles + files

        challenge.files = allfiles
        return challenge

    def download_challenge_files(self, challenge: Challenge, output_dir: Path):
        download_files(self, challenge, output_dir)

    def generate_tags(self, challenge):
        tags = []
        tags.append(challenge.category)
        tags.append("ImaginaryCTF")
        tags = list(set(filter(None, tags)))
        tags_str = '", "'.join(tags)
        return tags_str

    def generate_template(self, challenge: Challenge, hugo_header: bool = False, translated: bool = False):
        """Generate writeup template for challenge"""

        tags_str = self.generate_tags(challenge)

        hugo_header_template = textwrap.dedent(
        f"""\
        ---
        title: "{challenge.name}"
        date: "{datetime.now().isoformat()}"
        tags: ["{tags_str}"]
        author: "Noham"
        summary: "Writeup for {challenge.name} from {challenge.platform}. A {challenge.points} points {challenge.category.lower()} challenge with {challenge.solved_number} solves."
        showToc: false
        TocOpen: false
        draft: false
        hidemeta: false
        comments: true
        disableHLJS: false
        disableShare: false
        hideSummary: false
        searchHidden: false
        ShowReadingTime: true
        ShowBreadCrumbs: true
        searchHidden: true
        ShowPostNavLinks: true
        ShowWordCount: true
        ShowRssButtonInSectionTermList: true
        UseHugoToc: true
        ---
        """
        )

        hugo_header_template_fr = textwrap.dedent(
        f"""\
        ---
        title: "{challenge.name}"
        date: "{datetime.now().isoformat()}"
        tags: ["{tags_str}"]
        author: "Noham"
        summary: "Writeup du challenge {challenge.name} de {challenge.platform}. Un challenge de {challenge.category.lower()} de {challenge.points} points avec {challenge.solved_number} résolutions."
        showToc: false
        TocOpen: false
        draft: false
        hidemeta: false
        comments: true
        disableHLJS: false
        disableShare: false
        hideSummary: false
        searchHidden: false
        ShowReadingTime: true
        ShowBreadCrumbs: true
        searchHidden: true
        ShowPostNavLinks: true
        ShowWordCount: true
        ShowRssButtonInSectionTermList: true
        UseHugoToc: true
        ---
        """
        )

        stars = "⭐" * min(5, max(1, round(challenge.points / 40)))
        
        files_section = ""
        for file in challenge.files:
            hash_text = f" *(SHA256: {file.hash})*" if file.hash else ""
            files_section += f"[{file.name}]({file.url}){hash_text}, "
        files_section = files_section.rstrip(", ")

        main_content = textwrap.dedent(
        f"""\
        - Challenge URL: [{challenge.name} - {challenge.platform}]({challenge.url})
        - Author: {challenge.author}
        - Category: {challenge.category}
        - Challenge description: {challenge.description}
        - Difficulty: {stars} ({challenge.points} points, {challenge.solved_number} solves)
        - Files provided: {files_section}

        ## Writeup 
        """
        )

        main_content_fr = textwrap.dedent(
        f"""\
        - URL du challenge: [{challenge.name} - {challenge.platform}]({challenge.url})
        - Auteur: {challenge.author}
        - Catégorie: {challenge.category}
        - Description du challenge: {challenge.description}
        - Difficulté: {stars} ({challenge.points} points, {challenge.solved_number} résolutions)
        - Fichiers fournis: {files_section}

        ## Writeup
        """
        )

        if hugo_header:
            challenge.template = hugo_header_template + main_content
            if translated:
                challenge.template_translated = hugo_header_template_fr + main_content_fr
        else:
            challenge.template = main_content
            if translated:
                challenge.template_translated = main_content_fr