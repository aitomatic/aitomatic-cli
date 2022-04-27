import click
from src.login.main import authenticated


@click.command()
@authenticated
def apps():
    '''Listing apps in Aitomatic cluster'''
    click.echo(f'Connect to Aitomatic cloud')
    click.echo(f'Listing apps ...\n')

    click.echo(click.style(f'id\tname\t\tver\tstatus', fg='green', bold='true'))
    click.echo(f'1\tfixed-net\t0.1.9\trunning')
    click.echo(f'2\tvessel-based\t0.0.8\tstopped')
