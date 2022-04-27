import click
from src.list.jobs import jobs
from src.list.apps import apps


@click.group()
def list():
    '''CLI sub-command to help manage aitomatic cluster'''

list.add_command(jobs)
list.add_command(apps)
