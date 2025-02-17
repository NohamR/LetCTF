from pathlib import Path
from typing import List
from .platforms.base import CTFPlatform
from .models import Challenge

class WriteupGenerator:
    """Main class to handle writeup generation"""
    def __init__(self, platform: CTFPlatform, output_dir: Path):
        self.platform = platform
        self.output_dir = output_dir
        self.challenges = []

    def fetch_challenges(self):
        """Fetch all challenges from the platform"""
        self.challenges = self.platform.get_challenges()

    def fetch_challenge(self, challenge_url: str) -> Challenge:
        """Fetch a specific challenge"""
        self.challenges = [] if not self.challenges else self.challenges
        challenge = self.platform.get_challenge(challenge_url)
        self.challenges.append(challenge)

    def generate_writeup_structure(self, hugo_header: bool = False, translated: bool = False):
        """Generate folder structure and writeup templates"""
        for challenge in self.challenges:
            platform_dir = self.output_dir / challenge.platform.lower()
            platform_dir.mkdir(parents=True, exist_ok=True)

            challenge_dir = platform_dir / self._sanitize_filename(challenge.id)
            challenge_dir.mkdir(exist_ok=True)

            files_dir = challenge_dir / "files"
            files_dir.mkdir(exist_ok=True)
            self.platform.download_challenge_files(challenge, files_dir)

            self.platform.generate_template(challenge, hugo_header, translated)

            if (challenge_dir / "index.md").exists():
                print(f"Writeup for {challenge.id} already exists. Skipping...")
                continue
            else:
                (challenge_dir / "index.md").write_text(challenge.template)

            if translated:
                if (challenge_dir / "index.fr.md").exists():
                    print(f"Writeup for {challenge.id} already exists. Skipping...")
                    continue
                else:
                    (challenge_dir / "index.fr.md").write_text(challenge.template_translated)


    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename for filesystem"""
        return "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).strip()