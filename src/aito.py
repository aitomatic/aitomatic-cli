import click
import json
from src.create.main import create
from src.execute.main import execute
from src.deploy.main import deploy
from src.list.main import list
from src.train.main import train
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
cli.add_command(create)
cli.add_command(execute)
cli.add_command(deploy)
cli.add_command(list)
cli.add_command(train)

if __name__ == '__main__':
    cli()
