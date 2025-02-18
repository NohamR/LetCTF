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

class RootMePlatform(CTFPlatform):
    def __init__(self, url: str = "https://www.root-me.org/", config_file: str | Path = None):
        super().__init__(url)
        self.url = url
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
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        }
        if config_file:
            self.load_config(config_file)
            self.login()

    def load_config(self, config_file: str | Path):
        """Load configuration from file"""
        config = load_config(config_file)
        self.email = config.get("email")
        self.password = config.get("password")


    def login(self) -> bool:
        """Login to platform"""
        params = (('page', 'login'),('lang', 'fr'),('ajah', '1'),)
        data = {'triggerAjaxLoad': '',}
        response = self.session.post('https://www.root-me.org/', headers=self.headers, params=params, data=data)
        soup = BeautifulSoup(response.text, 'html.parser')
        form_hidden = soup.find('span', class_='form-hidden')
        formulaire_action_args = form_hidden.find('input', {'name': 'formulaire_action_args'})['value']

        data = {'var_ajax': 'form','page': 'login','lang': 'fr','ajah': '1','formulaire_action': 'login','formulaire_action_args': formulaire_action_args,'formulaire_action_sign': '','var_login': self.email,'password': self.password}
        response = self.session.post('https://www.root-me.org/', headers=self.headers, params=params, data=data)
        if response.status_code == 200 and '>Vous êtes enregistré...' in response.text:
            print("Login successful")
            return True
        else:
            raise Exception("Login failed")

    
    def get_challenges(self) -> List[Challenge]:
        """Get all challenges from platform"""
        raise NotImplementedError("RootMePlatform does not support fetching all challenges")
    
    def get_challenge(self, challenge_url: str) -> Challenge:
        """Get a specific challenge by URL"""
        try:
            response = self.session.get(challenge_url, headers=self.headers)
            if response.status_code != 200:
                raise Exception(f"Error fetching challenges: {response.status_code}")
        except requests.RequestException as e:
            raise Exception(f"Error fetching challenges: {e}")
        
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('h1', {'class': 'challenge-titre-41'}).text.strip()
        
        id = title.lower().replace(' ', '-')
        author = soup.find('a', {'class': 'txt_0minirezo'}).text.strip()
        points = int(soup.find('h2', {'class': 'challenge-score-41'}).text.split()[0])
        description = soup.find('div', {'class': 'challenge-descriptif-41'}).text.strip()
        
        # category_img = soup.find('a', {'href': re.compile(r'fr/Challenges/[^/]+/')})
        # category = category_img['href'].split('/')[2] if category_img else "Uncategorized"
        category = challenge_url.split('/')[-2]

        difficulty_elements = soup.find_all('a', {'class': re.compile(r'difficulte.*')})
        difficulty = "Unknown"
        for elem in difficulty_elements:
            if 'a' in elem['class'][-1]:  # Check if the last class ends with 'a'
                difficulty = elem['title'].split(':')[0].strip()
                break
        
        files = []
        file_links = soup.find_all('a', {'class': 'button small radius'})
        for link in file_links:
            filename = link['href'].split('/')[-1]
            files.append(File(name=filename, url=link['href'], hash=None))
        
        validations = soup.find('a', {'title': 'Qui a validé ?'}).text.strip().split()[0]
        votes = soup.find('span', {'class': 'notation_valeur'}).text.strip().split()[0]
        
        completion_div = soup.find('span', {'class': 'left gras'})
        completion_rate = completion_div.text.strip().replace('%', '') if completion_div else "Unknown"
        
        solve_count = int(validations.replace(',', ''))
        additional_info = {
            'votes': int(votes),
            'completion_rate': completion_rate
        }

        return Challenge(
            id=id,
            url=challenge_url,
            platform="Root-Me",
            name=title,
            author=author,
            category=category,
            description=description,
            difficulty=difficulty,
            points=points,
            files=files,
            additional_info=additional_info,
            solved_number=solve_count,
        )

    def download_challenge_files(self, challenge: Challenge, output_dir: Path):
        download_files(self, challenge, output_dir)

    def generate_template(self, challenge: Challenge, hugo_header: bool = False, translated: bool = False):
        """Generate writeup template for challenge"""

        all_tags = list(set([challenge.category] + [challenge.platform]))
        tags_str = '", "'.join(all_tags)

        hugo_header_template = textwrap.dedent(
        f"""\
        ---
        title: "{challenge.name}"
        date: "{datetime.now().isoformat()}"
        tags: ["{tags_str}"]
        author: "Noham"
        summary: "Writeup for {challenge.name} from {challenge.platform}. A {challenge.category.lower()} challenge with a "{challenge.difficulty.lower()}" difficulty (sucess rate : {challenge.additional_info['completion_rate']}%)."
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
        summary: "Writeup pour {challenge.name} de {challenge.platform}. Un challenge {challenge.category.lower()} de difficulté "{challenge.difficulty.lower()}" (taux de réussite : {challenge.additional_info['completion_rate']}%)."
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

        difficulty_mapping = {
            'Très facile': 1,
            'Facile': 2,
            'Moyen': 3,
            'Difficile': 4,
            'Très difficile': 5
        }
        difficulty_level = difficulty_mapping.get(challenge.difficulty, 1)
        stars = "⭐" * difficulty_level
        
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
        - Difficulty: {stars} ({challenge.difficulty}, success rate: {challenge.additional_info['completion_rate']}%)
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
        - Difficulté: {stars} ({challenge.difficulty}, taux de réussite : {challenge.additional_info['completion_rate']}%)
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