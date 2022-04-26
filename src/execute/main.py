import click
from src.execute.app import app


@click.group()
def execute():
    '''Execute app/project deployed in Aitomatic cluster'''


execute.add_command(app)
