import click
from src.deploy.app import app


@click.group()
def deploy():
    '''Deploy app/project to Aitomatic cluster'''

deploy.add_command(app)
