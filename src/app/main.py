import click
from src.app.deploy import deploy


@click.group()
def app():
    '''CLI sub-command to help manage aitomatic apps'''


app.add_command(deploy)
