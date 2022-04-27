import click
from src.create.app import app
from src.create.project import project


@click.group()
def create():
    '''Create app/project to Aitomatic cluster'''

create.add_command(project)
create.add_command(app)
