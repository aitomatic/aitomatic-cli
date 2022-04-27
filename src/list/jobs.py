import click
from src.login.main import authenticated


@click.command()
@authenticated
def jobs():
    '''Listing jobs in Aitomatic cluster'''
    click.echo('Connect to Aitomatic cloud')
    click.echo('Listing jobs ...')
    
    click.echo(click.style(f'id\tname\t\t\t\tarch\t\tstatus', fg='green', bold='true'))
    click.echo(f'1\tk-swe-2022-04-27-werwre\t\tk-swe\t\trunning')
    click.echo(f'2\tk-oracle-2022-04-25-kmoods\tk-oracle\tstopped')
