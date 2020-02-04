import subprocess

import requests


def ocr_from_url(url: str) -> str:
    with requests.get(url) as img:
        return subprocess.run(['tesseract', 'stdin', 'stdout'], input=img.content, capture_output=True) \
            .stdout.decode('utf-8')
