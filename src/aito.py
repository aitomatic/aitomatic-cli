import click
from src.execute.main import execute
from src.deploy.main import deploy
from src.login.main import login
from src.logout.main import logout
from src.run.main import run
from src.list.main import list
from src.logs.main import logs
from src.constants import CREDENTIAL_FILE, AITOMATIC_PROFILE
from src.utils import read_ini_file


def load_config():
    if CREDENTIAL_FILE.exists():
        credentials = read_ini_file(CREDENTIAL_FILE)
        return credentials[AITOMATIC_PROFILE]
    else:
        return {}


AUTH_INFO = load_config()


@click.group(
    context_settings={'obj': AUTH_INFO},
)
@click.version_option(
    package_name='aitomatic', message='%(package)s (%(prog)s): Version %(version)s'
)
def cli():
    '''Aitomatic CLI tool to help manage aitomatic projects and apps'''


cli.add_command(login)
cli.add_command(logout)
cli.add_command(execute)
cli.add_command(deploy)
cli.add_command(run)
cli.add_command(list)
cli.add_command(logs)


if __name__ == '__main__':
    cli()
