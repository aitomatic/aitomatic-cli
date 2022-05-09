from os import getenv
from pathlib import Path


CREDENTIAL_FILE = Path.home().joinpath('.aitomatic/credentials')
AITOMATIC_PROFILE = getenv('AITOMATIC_PROFILE', 'default')
