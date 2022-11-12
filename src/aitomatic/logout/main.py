import click

from src.constants import CREDENTIAL_FILE


@click.command()
def logout():
    '''Logout from Aitomatic cloud'''
    remove_local_credential_file()
    click.echo('Logout successfully. Please login to use other commands.')


def remove_local_credential_file():
    if CREDENTIAL_FILE.exists():
        CREDENTIAL_FILE.unlink()
