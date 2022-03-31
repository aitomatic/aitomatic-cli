import click
from src.login.main import authenticated


@click.command()
@authenticated
def deploy():
    '''Deploy app to Aitomatic cluster'''
    click.echo('Deploy app to Aitomatic')
    # click.echo('User info', obj)
