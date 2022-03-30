import click
from src.login.cli import authenticated


@click.command()
@authenticated
def deploy():
    click.echo('Deploy app to Aitomatic')
    # click.echo('User info', obj)
