import click
from src.app.deploy import deploy
from src.app.execute import execute


@click.group()
def app():
    '''CLI sub-command to help manage aitomatic apps'''


app.add_command(deploy)
app.add_command(execute)
