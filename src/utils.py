from os import urandom
from base64 import urlsafe_b64encode
from hashlib import sha256
from re import sub

import string
import random


def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def create_code_verifier():
    code_verifier = urlsafe_b64encode(urandom(40)).decode('utf-8')
    code_verifier = sub('[^a-zA-Z0-9]+', '', code_verifier)

    return code_verifier


def create_code_challenger(code_verifier):
    code_challenge = sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = urlsafe_b64encode(code_challenge).decode('utf-8')
    code_challenge = code_challenge.replace('=', '')
    return code_challenge
