from typing import List, Dict
from pathlib import Path
import requests
from .base import CTFPlatform
from ..models import Challenge, File
from ..utils.config_handler import load_config
from ..utils.challenge_handler import download_files
from bs4 import BeautifulSoup
import unicodedata
from datetime import datetime
import textwrap


class HackropolePlatform(CTFPlatform):
    def __init__(
        self, url: str = "https://hackropole.fr", config_file: str | Path = None
    ):
        super().__init__(url)
        if config_file:
            self.load_config(config_file)
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "referer": "https://hackropole.fr/",
            "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        }

    def load_config(self, config_file: str | Path):
        """Load configuration from file"""
        config = load_config(config_file)
        self.token = config.get("token")
        self.provider = config.get("provider")

    def login(self) -> bool:
        """
        Not implementing traditional login as we're using cookies
        Returns True if we can access authenticated endpoints
        """
        try:
            data = {
                "token": self.token,
                "provider": self.provider,
            }
            response = self.session.post(
                "https://hackropole.fr/api/hackropole/user/self",
                headers=self.headers,
                json=data,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_challenges(self) -> List[Challenge]:
        raise NotImplementedError("Method not implemented")

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

        title = unicodedata.normalize(
            "NFKD", soup.select_one(".jumbotron h1").get_text(strip=True)
        )
        id = "-".join([word.lower() for word in title.split()])

        badges = [
            unicodedata.normalize("NFKD", badge.get_text(strip=True))
            for badge in soup.select(".jumbotron .badge")
            if "résolu le"
            not in unicodedata.normalize("NFKD", badge.get_text(strip=True))
        ]
        description = unicodedata.normalize(
            "NFKD", soup.select_one(".markdown p").get_text(strip=True)
        )

        file_links = []
        file_names = []
        file_hashes = {}
        file_elements = soup.select(".list-file li")
        for element in file_elements:
            link = element.select_one("a")["href"]
            name = (
                element.select_one("a").get("download")
                or element.select_one("a")["href"].split("/")[-1]
            )
            file_links.append(link)
            file_names.append(name)
            hash_element = element.select_one(".clip-sha256")
            if hash_element:
                hash_text = hash_element.get_text(strip=True)
                file_hash = hash_text.split("–")[-1].strip()
                file_hashes[name] = file_hash

        author_name = unicodedata.normalize(
            "NFKD",
            soup.select_one(".col.text-center .font-monospace").get_text(strip=True),
        )
        author_avatar = soup.select_one(".col.text-center img")["src"]

        stars = len(
            [
                star
                for star in soup.select("svg.text-warning")
                if star.select_one("title").get_text(strip=True) == "star"
            ]
        )

        available_categories = [
            "crypto",
            "forensics",
            "hardware",
            "misc",
            "pwn",
            "reverse",
            "web",
        ]
        for badge in badges:
            if badge.lower() in available_categories:
                category = badge
                break

        files = [
            File(name=file_name, hash=file_hashes.get(file_name), url=file_link)
            for file_name, file_link in zip(file_names, file_links)
        ]

        return Challenge(
            id=id,
            url=challenge_url,
            platform="Hackropole",
            name=title,
            author=author_name,
            category=category if category else "Uncategorized",
            description=description,
            difficulty=stars,
            points=None,
            files=files,
            additional_info={"badges": badges, "author_avatar": author_avatar},
        )

    def download_challenge_files(self, challenge: Challenge, output_dir: Path):
        download_files(self, challenge, output_dir)

    def generate_template(self, challenge: Challenge, hugo_header: bool = False, translated: bool = False):
        """Generate writeup template for challenge"""

        all_tags = list(set([challenge.category] + challenge.additional_info["badges"])) # Remove duplicates
        tags_str = '", "'.join(all_tags)

        hugo_header_template = textwrap.dedent(
        f"""\
        ---
        title: "{challenge.name}"
        date: "{datetime.now().isoformat()}"
        tags: ["{tags_str}"]
        author: "Noham"
        summary: "Writeup for {challenge.name} from {challenge.platform}. A {challenge.category} challenge with a difficulty of {challenge.difficulty if challenge.difficulty > 0 else 1}/5."
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
        summary: "Writeup pour {challenge.name} de {challenge.platform}. Un challenge de {challenge.category} avec une difficulté de {challenge.difficulty if challenge.difficulty > 0 else 1}/5."
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

        stars = "⭐" * (challenge.difficulty if challenge.difficulty > 0 else 1)
        
        files_section = ""
        for file in challenge.files:
            hash_text = f" *(SHA256: {file.hash})*" if file.hash else ""
            files_section += f"[{file.name}]({file.url}){hash_text}, "
        files_section = files_section.rstrip(", ")

        main_content = textwrap.dedent(
        f"""\
        - Author: {challenge.author}  
        - Category: {challenge.category}  
        - Difficulty: {stars} ({challenge.difficulty if challenge.difficulty > 0 else 1}/5)  
        - Challenge URL: [{challenge.name} - {challenge.platform}]({challenge.url})
        - Challenge description: {challenge.description}
        - Files provided: {files_section}

        ## Writeup 
        """
        )

        main_content_fr = textwrap.dedent(
        f"""\
        - Auteur: {challenge.author}
        - Catégorie: {challenge.category}
        - Difficulté: {stars} ({challenge.difficulty if challenge.difficulty > 0 else 1}/5)
        - URL du challenge: [{challenge.name} - {challenge.platform}]({challenge.url})
        - Description du challenge: {challenge.description}
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