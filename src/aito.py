import click
import json
from pathlib import Path
from src.app.main import app
from src.login.main import login

CONFIG_FILE = Path.home().joinpath('.aitomatic')


def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    else:
        return {}


AUTH_INFO = load_config()


@click.group(
    context_settings={'obj': AUTH_INFO},
)
def cli():
    '''Aitomatic CLI tool to help manage aitomatic projects and apps'''


cli.add_command(login)
cli.add_command(app)


if __name__ == '__main__':
    cli()
