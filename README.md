# CTF Writeup Generator

A Python tool to automatically generate CTF writeup templates and organize challenge files. Currently supports Hackropole platform with extensibility for other CTF platforms.

### Supported CTF Websites :
- https://hackropole.fr
- https://theblackside.fr
- https://crackmes.one

### Will add :
- https://imaginaryctf.org
- https://challenges.ecsc.eu/challenges
- https://www.root-me.org
- https://www.hackthissite.org

## Features

- Automated writeup template generation
- Challenge information scraping
- File downloading and organization
- Support for multiple CTF platforms
- Hugo-compatible markdown generation
- Multilingual support (English/French)
- Cookie-based and token-based authentication

## Installation

1. Clone the repository:
```bash
git clone https://github.com/nohamr/LetCTF.git
cd LetCTF
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

<!-- ## Configuration

### Authentication

The tool supports both cookie-based and token-based authentication. Create one or both of the following files:

1. `config.json` for token-based auth:
```json
{
    "token": "your-token-here"
}
```

2. `cookies.json` for cookie-based auth:
```json
{
    "session": "your-session-cookie",
    "other_cookie": "other-cookie-value"
}
``` -->

## Usage

### Basic Usage

```python
from pathlib import Path
from src.platforms.hackropole import HackropolePlatform
from src.generator import WriteupGenerator

# Initialize platform with auth if needed
platform = HackropolePlatform(
    config_file="config.json",
    cookie_file="cookies.json"
)

# Create generator
generator = WriteupGenerator(platform, Path("./writeups"))

# Generate writeups
generator.fetch_challenges()
generator.generate_writeup_structure(
    hugo_header=True,  # Include Hugo front matter
    translated=True    # Generate French translations
)
```

### Output Structure

```
writeups/
├── Platform1/
│   ├── Challenge1/
│   │   ├── index.md
│   │   ├── index.fr.md
│   │   └── challenge_files/
│   └── Challenge2/
└── Platform2/
    └── Challenge3/
```

## Adding New Platforms

1. Create a new platform file in `src/platforms/`:
```python
from .base import CTFPlatform
from ..models import Challenge

class NewPlatform(CTFPlatform):
    def login(self, credentials: Dict) -> bool:
        # Implement login
        pass

    def get_challenges(self) -> List[Challenge]:
        # Implement challenge fetching
        pass

    def get_challenge(self) -> Challenge:
        # Implement specific challenge by URL
        pass

    def generate_template(self, challenge: Challenge, hugo_header: bool = False, translated: bool = False):
        # Implement generating writeup template for challenge
        pass
```

2. Use the new platform:
```python
from src.platforms.new_platform import NewPlatform

platform = NewPlatform()
```

## Template Format

The generated writeup templates include:
- Challenge metadata (author, category, difficulty)
- Challenge description
- File information with hashes
- Basic writeup structure
- Hugo front matter (optional)

Example template:
```markdown
---
title: "Challenge Name"
date: "1970-00-00T00:00:00"
tags: ["category", "badge1", "badge2"]
author: "Author"
---

- Author: Challenge Author
- Category: Web
- Difficulty: ⭐⭐⭐ (3/5)
- Challenge URL: [Challenge Name - Platform](https://platform/challenges/123)
- Files provided: [file.zip](https://url/file.zip) *(SHA256: hash)*

## Writeup
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.