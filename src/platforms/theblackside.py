from typing import List, Dict
from pathlib import Path
import requests
from .base import CTFPlatform
from ..models import Challenge, File
from ..utils.cookie_handler import load_cookies_from_file
from ..utils.challenge_handler import download_files
from bs4 import BeautifulSoup
from datetime import datetime
import textwrap
import re

class TheBlackSidePlatform(CTFPlatform):
    def __init__(
        self, url: str = "https://theblackside.fr/", cookies_file: str | Path = None
    ):
        super().__init__(url)
        if cookies_file:
            self.cookie = load_cookies_from_file(cookies_file)
        else:
            raise Exception("No cookies provided")
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "referer": "https://theblackside.fr/",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"macOS\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }
        self.login()

    def login(self) -> bool:
        """
        Not implementing traditional login as we're using cookies
        Login is protected using Google reCAPTCHA..
        Returns True if we can access authenticated endpoints
        """
        try:
            response = self.session.get(
                "https://theblackside.fr/",
                headers=self.headers,
                cookies=self.cookie,
            )
            if "/profil/" in response.text:
                print("Logged in")
            else:
                raise Exception("Failed to login")
        except requests.exceptions.RequestException:
            raise Exception("Failed to login")
        
    def get_challenges(self) -> List[Challenge]:
        raise NotImplementedError("Method not implemented")

    def get_challenge(self, challenge_url: str) -> Challenge:
        """Get a specific challenge by URL"""
        try:
            response = self.session.get(challenge_url, headers=self.headers, cookies=self.cookie)
            if response.status_code != 200:
                raise Exception(
                    f"Error fetching challenge {challenge_url}: {response.status_code}"
                )
        except requests.RequestException as e:
            raise Exception(f"Error fetching challenge {challenge_url}: {e}")
        
        response.encoding = "utf-8"  # Force UTF-8 encoding
        soup = BeautifulSoup(response.text, "html.parser")

        main = soup.find('main')

        title = main.find('h1').text.strip()
        id = "-".join([word.lower() for word in title.split()])
        description = main.find('p').text.strip()
        
        author_link = main.find('a', href=re.compile(r'/profil/'))
        author_name = author_link.find('span').find('a').text.strip() if author_link else None
        
        metadata_div = main.find('div', class_='metadata')
        points = int(metadata_div.find('div', class_='button').find('span').text.strip())
        solved_number = int([div for div in metadata_div.find_all('div', class_='button') 
                            if div.find('svg', class_='feather-check-circle')][0]
                        .find('span').text.strip())
        
        category_button = metadata_div.find('a', href=re.compile(r'/challenges/'))
        category = category_button.find('span').text.strip() if category_button else "Uncategorized"

        categorydict = {
            "Web": "Web",
            "Stéganographie": "Steganography",
            "Cryptographie": "Cryptography",
            "Reverse": "Reverse",
            "Réseau": "Network",
            "Forensic": "Forensic",
            "Développement": "Development",
            "Pwn": "Pwn",
            "Box": "Box",
            "Divers": "Miscellaneous",
        }
        category = categorydict.get(category, category)

        
        file_url = main.find('a', class_='startChall')['href']

        file = File(
            name=file_url.split('/')[-1],
            url=file_url,
            hash=None,
        )


        return Challenge(
            id=id,
            url=challenge_url,
            platform="TheBlackSide",
            name=title,
            author=author_name,
            category=category if category else "Uncategorized",
            description=description,
            difficulty=None,
            solved_number=solved_number,
            points=points,
            files=[file],
        )

    
    def download_challenge_files(self, challenge: Challenge, output_dir: Path):
        download_files(self, challenge, output_dir)

    def generate_template(self, challenge: Challenge, hugo_header: bool = False, translated: bool = False):
        """Generate writeup template for challenge"""
        
        tags = [challenge.category, "TheBlackSide"]
        tags_str = ", ".join(tags)

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
        summary: "Writeup pour {challenge.name} de {challenge.platform}. Un challenge de {challenge.category.lower()} à {challenge.points} points avec {challenge.solved_number} résolutions."
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

        stars = "⭐" * min(5, max(1, round(challenge.points / 12)))
        
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
        - Points: {challenge.points} {stars}
        - Solved by: {challenge.solved_number} users
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
        - Points: {challenge.points} {stars}
        - Résolu par: {challenge.solved_number} utilisateurs
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