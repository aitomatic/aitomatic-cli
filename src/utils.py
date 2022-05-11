from base64 import urlsafe_b64encode
from configparser import ConfigParser
from click import secho
from os import urandom
from hashlib import sha256
from pathlib import Path
from re import sub

import string
import random


def get_random_string(length: int) -> str:
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def create_code_verifier():
    code_verifier = urlsafe_b64encode(urandom(40)).decode('utf-8')
    code_verifier = sub('[^a-zA-Z0-9]+', '', code_verifier)

    return code_verifier


def create_code_challenger(code_verifier: str) -> str:
    code_challenge = sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = urlsafe_b64encode(code_challenge).decode('utf-8')
    code_challenge = code_challenge.replace('=', '')
    return code_challenge


def read_ini_file(file_path: Path) -> dict:
    parser = ConfigParser()
    result = {}

    parser.read_string(file_path.read_text())
    for section in parser.sections():
        result[section] = {}
        for name, value in parser.items(section):
            result[section][name] = value

    return result


def show_error_message(message: str) -> None:
    secho(message, bold=True, fg='red')
