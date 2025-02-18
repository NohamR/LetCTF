from src.platforms.hackropole import HackropolePlatform
from src.platforms.theblackside import TheBlackSidePlatform
from src.platforms.crackmes import CrackmesPlatform
from src.platforms.crackmy import CrackmyPlatform
from src.platforms.cattheflag import CatTheFlagPlatform
from src.generator import WriteupGenerator
from pathlib import Path

def hackropole():
    challenge_url = 'https://hackropole.fr/fr/challenges/reverse/fcsc2023-reverse-chaussette-xs/'
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

def crackmy():
    challenge_url = 'https://crackmy.app/crackmes/yet-another-packer-v1-5514'
    # platform = CrackmyPlatform(config_file="crackmy.json")
    platform = CrackmyPlatform()

    generator = WriteupGenerator(platform, Path("./writeups"))
    generator.fetch_challenge(challenge_url=challenge_url)
    print(generator.challenges)
    generator.generate_writeup_structure(hugo_header=True, translated=True)

def cattheflag():
    challenge_url = 'https://cattheflag.org/defis/reverse2.php'
    platform = CatTheFlagPlatform(config_file="catthefile.json")

    generator = WriteupGenerator(platform, Path("./writeups"))
    generator.fetch_challenges() # Mandatory to get every information about a specific challenge for this platform
    generator.fetch_challenge(challenge_url=challenge_url)
    print(generator.challenges)
    generator.generate_writeup_structure(hugo_header=True, translated=True)


# theblackside()
# hackropole()
# crackmes()
# crackmy()
# cattheflag()