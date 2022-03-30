import click
import json
from pathlib import Path
from src.app.cli import app
from src.login.cli import login

CONFIG_FILE = Path.home().joinpath('.aitomatic')

def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    else:
        return None

AUTH_INFO = load_config()

@click.group(help='''
    Aitomatic CLI tool to help manage aitomatic projects and apps
''', context_settings={'obj': AUTH_INFO})
def cli():
    pass

cli.add_command(app)
cli.add_command(login)

if __name__ == '__main__':
    cli()
