from typing import List, Dict
from pathlib import Path
import requests
from .base import CTFPlatform
from ..models import Challenge, File
from ..utils.challenge_handler import download_files
from bs4 import BeautifulSoup
from datetime import datetime
import textwrap
import re

class CrackmesPlatform(CTFPlatform):
    def __init__(self, url: str = "https://crackmes.one"):
        super().__init__(url)
        self.headers = {}

    def login(self) -> bool:
        """Not implementing login since we don't need it :D"""
        return True
    
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

        container = soup.find('div', class_='container grid-lg wrapper')

        download_link = soup.find('a', class_='btn-download')

        author_element = container.find('a', href=re.compile(r'/user/'))
        author_name = author_element.text if author_element else None
        
        title_element = container.find('h3')
        name = title_element.text.strip().replace("{author_name}'s ".format(author_name=author_name), "") if title_element else None

        id = f"{name}-{author_name}"
        
        
        description_element = container.find('span', style='white-space: pre-line')
        description = description_element.text.strip() if description_element else None
        
        difficulty_element = container.find('p', text=re.compile('Difficulty:'))
        difficulty = float(difficulty_element.text.replace('Difficulty:', '').strip()) if difficulty_element else None
        
        if download_link:
            file = File(
                name = download_link['href'].split('/')[-1],
                url = "https://crackmes.one" + download_link['href'],
                hash=None,
            )
        
        columns = container.find_all('div', class_='column')
        
        def get_text_after_br(element):
            if not element:
                return None
            br = element.find('br')
            if br and br.next_sibling:
                return br.next_sibling.strip()
            return None
        
        platform = None
        language = None
        architecture = None
        quality = None
        difficulty = None
        
        for column in columns:
            p_tag = column.find('p')
            if not p_tag:
                continue
                
            text = p_tag.text.strip()
            if text.startswith('Language:'):
                language = get_text_after_br(p_tag)
            elif text.startswith('Platform'):
                platform = get_text_after_br(p_tag)
            elif text.startswith('Arch:'):
                architecture = get_text_after_br(p_tag)
            elif text.startswith('Quality:'):
                quality_text = get_text_after_br(p_tag)
                if quality_text:
                    try:
                        quality = float(quality_text)
                    except ValueError:
                        quality = None
            elif text.startswith('Difficulty:'):
                difficulty_text = get_text_after_br(p_tag)
                if difficulty_text:
                    try:
                        difficulty = float(difficulty_text)
                    except ValueError:
                        difficulty = None
        
        additional_info = {
            'platform': platform,
            'language': language,
            'architecture': architecture,
            'quality': quality,
        }

        print('additional_info: ', additional_info)

        return Challenge(
            id=id,
            url=challenge_url,
            platform="Crackmes",
            name=name,
            author=author_name,
            category="Reverse",
            description=description,
            difficulty=difficulty,
            points=None,
            files=[file],
            additional_info=additional_info,
        )

        
    def download_challenge_files(self, challenge: Challenge, output_dir: Path):
        download_files(self, challenge, output_dir, password="crackmes.one")

    def get_difficulty_str(self, difficulty):
        if difficulty is None:
            return None
        if difficulty < 2:
            return "easy"
        elif difficulty < 3:
            return "medium"
        elif difficulty < 4:
            return "hard"
        else:
            return "very hard"
        
    def generate_tags(self, challenge):
        tags = []
        tags.append(challenge.category)
        tags.append("Crackmes")
        if challenge.additional_info["platform"]:
            tags.append(challenge.additional_info["platform"])
        if challenge.additional_info["language"]:
            tags.append(challenge.additional_info["language"])
        if challenge.additional_info["architecture"]:
            tags.append(challenge.additional_info["architecture"])
        tags = list(set(filter(None, tags)))
        tags_str = '", "'.join(tags)
        return tags_str

    def generate_template(self, challenge: Challenge, hugo_header: bool = False, translated: bool = False):
        """Generate writeup template for challenge"""
        
        tags_str = self.generate_tags(challenge)

        difficulty_str = self.get_difficulty_str(challenge.difficulty)

        hugo_header_template = textwrap.dedent(
        f"""\
        ---
        title: "{challenge.name}"
        date: "{datetime.now().isoformat()}"
        tags: ["{tags_str}"]
        author: "Noham"
        summary: "Writeup for {challenge.name} from {challenge.platform}. A "{difficulty_str}" challenge."
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
        summary: "Writeup pour {challenge.name} de {challenge.platform}. Un challenge {difficulty_str}."
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
        - Difficulty: {challenge.difficulty}/5
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
        - Difficulté: {challenge.difficulty}/5
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