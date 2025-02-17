from src.platforms.hackropole import HackropolePlatform
from src.platforms.theblackside import TheBlackSidePlatform
from src.platforms.crackmes import CrackmesPlatform
from src.generator import WriteupGenerator
from pathlib import Path

def hackropole():
    challenge_url = 'https://hackropole.fr/fr/challenges/reverse/fcsc2023-reverse-chaussette-xs/'
    # challenge_url = 'https://hackropole.fr/fr/challenges/crypto/fcsc2022-crypto-t-rex/'
    # challenge_url = 'https://hackropole.fr/fr/challenges/crypto/fcsc2022-crypto-a-laise/'

    platform = HackropolePlatform()
    
    generator = WriteupGenerator(platform, Path("./writeups"))
    generator.fetch_challenge(challenge_url=challenge_url)
    print(generator.challenges)
    generator.generate_writeup_structure(hugo_header=True, translated=True)

def theblackside():
    challenge_url = 'https://theblackside.fr/challenges/steganographie/Meow'
    platform = TheBlackSidePlatform(cookies_file="theblackside.cookies.json")
    
    generator = WriteupGenerator(platform, Path("./writeups"))
    generator.fetch_challenge(challenge_url=challenge_url)
    generator.generate_writeup_structure(hugo_header=True, translated=True)

def crackmes():
    challenge_url = 'https://crackmes.one/crackme/6784f8a84d850ac5f7dc5173'
    platform = CrackmesPlatform()

    generator = WriteupGenerator(platform, Path("./writeups"))
    generator.fetch_challenge(challenge_url=challenge_url)
    print(generator.challenges)
    generator.generate_writeup_structure(hugo_header=True, translated=True)

# theblackside()
# hackropole()
crackmes()