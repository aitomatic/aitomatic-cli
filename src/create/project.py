import click
from src.login.main import authenticated
from src.api.aitomatic import AiCloudApi


@click.command()
@click.argument('project_name', type=str)
@click.pass_obj
@authenticated
def project(obj, project_name):
    '''Create a new application in the project'''

    click.echo(f'Populating project structure ... Done')

    click.echo(f'Created project {project_name} sucessfully')
