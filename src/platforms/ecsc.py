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

class ECSCPlatform(CTFPlatform):
    def __init__(self, url: str = "https://challenges.ecsc.eu"):
        super().__init__(url)
        self.headers = {
            'Accept': 'text/css,*/*;q=0.1',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://challenges.ecsc.eu/',
            'Sec-Fetch-Dest': 'style',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }

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


        title = soup.find('h1', class_='documentFirstHeading').text.strip()
        id = title.lower().replace(' ', '-')  # Using lowercase title as ID
        
        description_elem = soup.find('span', text='Description').find_next('span')
        description = description_elem.text.strip() if description_elem else ""
        
        difficulty_elem = soup.find('span', text='Difficulty').find_next('div', class_='difficulty')
        difficulty = difficulty_elem.find('span').text.strip() if difficulty_elem else "Unknown"
        
        provider_elem = soup.find('span', text='Provider').find_next('span')
        author = provider_elem.text.strip() if provider_elem else "Unknown"
        
        tags_elem = soup.find('span', text='Tags').find_next('span', class_='challenge-tags')
        category = tags_elem.find('span').text.strip() if tags_elem else "Uncategorized"
        
        files = []
        # write_ups_elem = soup.find('span', text='Write-ups').find_next('ul', class_='other-artefacts')
        # if write_ups_elem:
        #     for file in write_ups_elem.find_all('a'):
        #         files.append({
        #             'name': file.text.strip(),
        #             'url': file['href']
        #         })
        
        other_files_elem = soup.find('span', text='Other artefacts').find_next('ul', class_='other-artefacts')
        if other_files_elem:
            for file in other_files_elem.find_all('a'):
                files.append(File(name=file.text.strip(), url=file['href']))
        
        additional_info_elem = soup.find('span', text='Additional Info').find_next('span')
        additional_info = {
            'event': soup.find('span', text='Event').find_next('span').text.strip(),
            'extra': additional_info_elem.text.strip() if additional_info_elem else ""
        }
        
        return Challenge(
            id=id,
            url=challenge_url,
            platform="ECSC",
            name=title,
            author=author,
            category=category,
            description=description,
            difficulty=difficulty,
            points=None,
            files=files,
            additional_info=additional_info
        )
        
    def download_challenge_files(self, challenge: Challenge, output_dir: Path):
        download_files(self, challenge, output_dir)

    def generate_tags(self, challenge):
        tags = []
        tags.append(challenge.category)
        tags.append(challenge.platform)
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
        summary: "Writeup for {challenge.name} from {challenge.platform}. A {challenge.category.lower()} challenge with a "{challenge.difficulty.lower()}" difficulty."
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
        summary: "Writeup pour {challenge.name} de {challenge.platform}. Un challenge {challenge.category.lower()} de difficulté {challenge.difficulty.lower()}."
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

        difficulty_map = {"Easy": 1, "Medium": 2, "Hard": 3}
        star_count = difficulty_map.get(challenge.difficulty, 1)
        stars = "⭐" * star_count
        
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
        - Difficulty: {stars} ({challenge.difficulty})
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
        - Difficulté: {stars} ({challenge.difficulty})
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