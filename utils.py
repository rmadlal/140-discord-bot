import subprocess


def ocr(data: bytes) -> str:
    return subprocess.run(['tesseract', 'stdin', 'stdout'], input=data, capture_output=True).stdout.decode('utf-8')
