import click
import json
from pathlib import Path
from src.execute.main import execute
from src.deploy.main import deploy
from src.login.main import login, CREDENTIAL_FILE


def load_config():
    if CREDENTIAL_FILE.exists():
        return json.loads(CREDENTIAL_FILE.read_text())
    else:
        return {}


AUTH_INFO = load_config()


@click.group(
    context_settings={'obj': AUTH_INFO},
)
def cli():
    '''Aitomatic CLI tool to help manage aitomatic projects and apps'''


cli.add_command(login)
cli.add_command(execute)
cli.add_command(deploy)


if __name__ == '__main__':
    cli()
