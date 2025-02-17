from src.platforms.hackropole import HackropolePlatform
from src.generator import WriteupGenerator
from pathlib import Path

challenge_url = 'https://hackropole.fr/fr/challenges/reverse/fcsc2023-reverse-chaussette-xs/'
# challenge_url = 'https://hackropole.fr/fr/challenges/crypto/fcsc2022-crypto-t-rex/'
# challenge_url = 'https://hackropole.fr/fr/challenges/crypto/fcsc2022-crypto-a-laise/'

def main():
    platform = HackropolePlatform()
    
    generator = WriteupGenerator(platform, Path("./writeups"))
    generator.fetch_challenge(challenge_url=challenge_url)
    print(generator.challenges)
    generator.generate_writeup_structure(hugo_header=True, translated=True)

if __name__ == "__main__":
    main()