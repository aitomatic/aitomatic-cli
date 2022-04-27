import click

from src.constants import CREDENTIAL_FILE


@click.command()
@click.pass_obj
def logout(obj):
    '''Logout from Aitomatic cloud'''
    if obj.get('access_token') is not None:
        obj['access_token'] = None
        obj['refresh_token'] = None
        obj['id'] = None
    if CREDENTIAL_FILE.exists():
        CREDENTIAL_FILE.unlink()
    click.echo('Logout successfully. Please login to use other commands.')
