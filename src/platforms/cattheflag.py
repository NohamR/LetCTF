from typing import List, Dict
from pathlib import Path
from .base import CTFPlatform
from ..models import Challenge, File
from ..utils.config_handler import load_config
from ..utils.challenge_handler import download_files
from bs4 import BeautifulSoup
import unicodedata
from datetime import datetime
import textwrap
import requests
import re
from pprint import pprint

class CatTheFlagPlatform(CTFPlatform):
    def __init__(self, url: str = "https://cattheflag.org", config_file: str | Path = None):
        super().__init__(url)
        self.url = url
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://cattheflag.org',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://cattheflag.org/connexion.php',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        }
        if config_file:
            self.load_config(config_file)
            self.csrf_token = self.get_csrf_token()
            self.login()
        else:
            raise Exception("No configuration file provided")

    def get_csrf_token(self) -> str:
        try:
            response = self.session.get('https://cattheflag.org/connexion.php', headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
            return csrf_token
        except requests.RequestException:
            return None

    def load_config(self, config_file: str | Path):
        """Load configuration from file"""
        config = load_config(config_file)
        self.email = config.get("email")
        self.password = config.get("password")

    def login(self) -> bool:
        data = {
        'csrf_token': self.csrf_token,
        'email': self.email,
        'mot_de_passe': self.password,
        }
        response = self.session.post('https://cattheflag.org/connexion.php', headers=self.headers, data=data)
        if response.status_code != 200:
            raise f"Error logging in: {response.status_code}"
        else:
            print("Successfully logged in")
            return True


    def get_challenges(self) -> List[Challenge]:
        """Get all challenges from platform"""
        try:
            response = self.session.get('https://cattheflag.org/defis.php', headers=self.headers)
            if response.status_code != 200:
                raise Exception(f"Error fetching challenges: {response.status_code}")
        except requests.RequestException as e:
            raise Exception(f"Error fetching challenges: {e}")
        
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, 'html.parser')
        challenges = {}
        
        challenge_sections = soup.find_all('div', class_='challeng__wrap')
        
        for section in challenge_sections:
            category = section.find('h3').text.strip()
            if category != 'Histoire':
                table = section.find('table')
                rows = table.find_all('tr')[1:]
                
                for row in rows:
                    cols = row.find_all(['th', 'td'])
                    
                    link = cols[3].find('a')
                    url = link['href'] if link else None
                
                    challenge_name = cols[0].text.strip()
                    challenge_id = url.split('/')[-1].replace('.php', '') if url else re.sub(r'[^a-zA-Z0-9]', '-', challenge_name.lower())

                    challenge_url = self.base_url + url
                    challenges[challenge_url] = Challenge(
                        id=challenge_id,
                        url=challenge_url,
                        platform="CatTheFlag",
                        name=challenge_name,
                        author=None,
                        category=category,
                        description=None,
                        difficulty=cols[1].text.strip(),
                        points=int(cols[2].text.strip()),
                        files=None,
                        additional_info={'validation_rate': float(cols[4].text.strip().replace('%', ''))}
                    )
        self.challenges = challenges
    
    def get_challenge(self, challenge_url: str) -> Challenge:
        """Get a specific challenge by URL"""
        try:
            response = self.session.get(challenge_url, headers=self.headers)
            if response.status_code != 200:
                raise Exception(
                    f"Error fetching challenge {challenge_url}: {response.status_code}"
                )
        except requests.RequestException as e:
            raise Exception(f"Error fetching challenge {challenge_url}: {e}")
        
        response.encoding = "utf-8"  # Force UTF-8 encoding
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find('h1').text.strip()
    
        description = soup.find('p', style='color:white').text.strip()
        
        author_link = soup.find('a', href=lambda x: x and 'page_membre.php' in x)
        author_name = author_link.text.strip() if author_link else None
        
        file_link = soup.find('a', href=lambda x: x and 'cdn.cattheflag.org' in x)
        if file_link:
            files = [File(
                name=file_link['href'].split('/')[-1],
                url=file_link['href'],
                hash=None
            )]
        else:
            files = []

        challenge = self.challenges.get(challenge_url)
        challenge.description = description
        challenge.author = author_name
        challenge.files = files
        return challenge

    def download_challenge_files(self, challenge: Challenge, output_dir: Path):
        download_files(self, challenge, output_dir)

    def generate_tags(self, challenge):
        tags = []
        tags.append(challenge.category)
        tags.append("CatTheFlag")
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
        summary: "Writeup for {challenge.name} from {challenge.platform}. A {challenge.category.lower()} challenge with a "{challenge.difficulty.lower()}" difficulty (sucess rate : {challenge.additional_info['validation_rate']}%)."
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
        summary: "Writeup pour {challenge.name} de {challenge.platform}. Un challenge de {challenge.category.lower()} avec une difficulté {challenge.difficulty.lower()} (taux de réussite : {challenge.additional_info['validation_rate']}%)."
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

        difficulty_stars = {
            'facile': 1,
            'simple': 2,
            'medium': 3,
            'difficile': 4
        }
        stars = "⭐" * difficulty_stars.get(challenge.difficulty.lower(), 1)
        
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
        - Difficulty: {stars} ({challenge.difficulty}, success rate: {challenge.additional_info['validation_rate']}%)
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
        - Difficulté: {stars} ({challenge.difficulty}, taux de réussite : {challenge.additional_info['validation_rate']}%)
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