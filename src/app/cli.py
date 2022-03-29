import click
from src.app.deploy import deploy


@click.group(
    help='''
    CLI sub-command to help manage aitomatic apps
'''
)
def app():
    pass


app.add_command(deploy)
