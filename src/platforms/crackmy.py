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

class CrackmyPlatform(CTFPlatform):
    def __init__(self, url: str = "https://crackmy.app", config_file: str | Path = None):
        super().__init__(url)
        self.url = url
        if config_file:
            self.load_config(config_file)
            self.csrf_token = self.get_csrf_token()
            self.login()
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
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

    def get_csrf_token(self) -> str:
        try:
            response = self.session.get('https://crackmy.app/api/auth/csrf', headers=self.headers)
            return response.json()['csrfToken']
        except requests.RequestException:
            return None

    def load_config(self, config_file: str | Path):
        """Load configuration from file"""
        config = load_config(config_file)
        self.email = config.get("email")
        self.password = config.get("password")

    def login(self) -> bool:
        data = {
            'email': self.email,
            'password': self.password,
            'remember': 'false',
            'redirect': 'false',
            'csrfToken': self.csrf_token,
            'callbackUrl': 'https://crackmy.app/',
            'json': 'true'
        }
        try:
            response = self.session.post('https://crackmy.app/api/auth/callback/credentials', headers=self.headers, data=data).json()
            if response['url'] != "https://crackmy.app/api/auth/error?error=CredentialsSignin&provider=credentials":
                return True
            else:
                return False
        except requests.RequestException:
            return False

    def get_challenges(self) -> List[Challenge]:
        raise NotImplementedError("Method not implemented")

    def get_challenge(self, challenge_url: str) -> Challenge:
        """Get a specific challenge by URL"""

        api_url = challenge_url.replace('https://crackmy.app/crackmes/', 'https://crackmy.app/api/crackmes/')

        try:
            response = self.session.get(api_url, headers=self.headers)
            if response.status_code != 200:
                raise Exception(
                        f"Error fetching challenge {challenge_url}: {response.status_code}"
                    )
        except requests.RequestException as e:
            raise Exception(f"Error fetching challenge {challenge_url}: {e}")

        response = response.json()
        title = response['title']
        id = title.replace(' ', '-').lower()
        author_name = response['author']['name']
        description = response['description']

        additional_info = {
            'platform': response['os'],
            'architecture': response['architecture'],
            'quality': response['qualityRating'],
            'category': response['category'],
            'rating': response['rating'],
        }

        difficulty = {
            "difficulty": response["difficulty"],
            "difficultyRating": response["difficultyRating"],
        }

        try:
            data = {"fileId":response['file']["id"]}
            download_request = self.session.post('https://crackmy.app/api/download/create', headers=self.headers, json=data).json()
        except requests.RequestException as e:
            raise Exception(f"Error fetching challenge {challenge_url}: {e}")
        file_url = self.base_url + download_request['url']

        files = [
            File(
                name=response["file"]["fileName"],
                url=file_url,
                hash=response["file"]["fileSha256"],
            )
        ]

        return Challenge(
            id=id,
            url=challenge_url,
            platform="Crackmy",
            name=title,
            author=author_name,
            category="Reverse",
            description=description,
            difficulty=difficulty,
            points=None,
            files=files,
            additional_info=additional_info,
        )

    def download_challenge_files(self, challenge: Challenge, output_dir: Path):
        download_files(self, challenge, output_dir)

    def generate_tags(self, challenge):
        tags = []
        tags.append(challenge.category)
        tags.append("Crackmy")
        if challenge.additional_info["platform"]:
            tags.append(challenge.additional_info["platform"])
        if challenge.additional_info["architecture"]:
            tags.append(challenge.additional_info["architecture"])
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
        summary: "Writeup for {challenge.name} from {challenge.platform}. A {challenge.category.lower()} challenge with a {challenge.difficulty['difficulty'].lower()} difficulty ({challenge.difficulty['difficultyRating'] if challenge.difficulty['difficultyRating'] > 0 else 0}/10)."
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
        summary: "Writeup pour {challenge.name} de {challenge.platform}. Un challenge de {challenge.category.lower()} avec une difficulté {challenge.difficulty['difficulty'].lower()} ({challenge.difficulty['difficultyRating'] if challenge.difficulty['difficultyRating'] > 0 else 0}/10)."
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

        stars = "⭐" * (int(challenge.difficulty['difficultyRating']) // 2 if challenge.difficulty['difficultyRating'] > 0 else 1)
        
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
        - Difficulty: {stars} ({challenge.difficulty['difficultyRating'] if challenge.difficulty['difficultyRating'] > 0 else 1}/10)
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
        - Difficulté: {stars} ({challenge.difficulty['difficultyRating'] if challenge.difficulty['difficultyRating'] > 0 else 1}/10)
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