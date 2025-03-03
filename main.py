from src.platforms.hackropole import HackropolePlatform
from src.platforms.theblackside import TheBlackSidePlatform
from src.platforms.crackmes import CrackmesPlatform
from src.platforms.crackmy import CrackmyPlatform
from src.platforms.cattheflag import CatTheFlagPlatform
from src.platforms.imaginaryctf import ImaginaryCTFPlatform
from src.platforms.rootme import RootMePlatform
from src.platforms.ecsc import ECSCPlatform
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
    platform = TheBlackSidePlatform(cookies_file="./config/theblackside.cookies.json")
    
    generator = WriteupGenerator(platform, Path("./writeups"))
    generator.fetch_challenge(challenge_url=challenge_url)
    print(generator.challenges)
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
    # platform = CrackmyPlatform(config_file="./config/crackmy.json")
    platform = CrackmyPlatform()

    generator = WriteupGenerator(platform, Path("./writeups"))
    generator.fetch_challenge(challenge_url=challenge_url)
    print(generator.challenges)
    generator.generate_writeup_structure(hugo_header=True, translated=True)

def cattheflag():
    challenge_url = 'https://cattheflag.org/defis/reverse2.php'
    platform = CatTheFlagPlatform(config_file="./config/catthefile.json")

    generator = WriteupGenerator(platform, Path("./writeups"))
    generator.fetch_challenges() # Mandatory to get every information about a specific challenge for this platform
    generator.fetch_challenge(challenge_url=challenge_url)
    print(generator.challenges)
    generator.generate_writeup_structure(hugo_header=True, translated=True)

def imaginaryctf():
    challenge_name = "Wrong ssh"
    challenge_url = challenge_name.lower().replace(' ', '-')
    platform = ImaginaryCTFPlatform()

    generator = WriteupGenerator(platform, Path("./writeups"))
    generator.fetch_challenges()
    generator.fetch_challenge(challenge_url=challenge_url)
    print(generator.challenges)
    generator.generate_writeup_structure(hugo_header=True, translated=True)

def rootme():
    challenge_url = 'https://www.root-me.org/fr/Challenges/Cracking/ELF-x86-0-protection'
    platform = RootMePlatform(config_file="./config/rootme.json")

    generator = WriteupGenerator(platform, Path("./writeups"))
    generator.fetch_challenge(challenge_url=challenge_url)
    print(generator.challenges)
    generator.generate_writeup_structure(hugo_header=True, translated=True)

def ecsc():
    challenge_url = 'https://challenges.ecsc.eu/challenges/binary'
    platform = ECSCPlatform()

    generator = WriteupGenerator(platform, Path("./writeups"))
    generator.fetch_challenge(challenge_url=challenge_url)
    print(generator.challenges)
    generator.generate_writeup_structure(hugo_header=True, translated=True)

# theblackside()
# hackropole()
# crackmes()
# crackmy()
# cattheflag()
# imaginaryctf()
# rootme()
# ecsc()