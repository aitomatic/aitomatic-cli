import click
from src.login.main import authenticated
from src.api.aitomatic import AiCloudApi


@click.command()
@click.argument('app_name', type=str)
@click.pass_obj
@authenticated
def app(obj, app_name):
    '''Create a new application in the project'''

    click.echo(f'Populating application structure for {app_name} ... Done')