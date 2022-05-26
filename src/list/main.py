import click
from src.api.aitomatic import AiCloudApi
from src.login.main import authenticated
from prettytable import PrettyTable


@click.command()
@click.argument('app_name', type=str)
@click.option('-n', 'n', default=10, help='Number of jobs')
@click.pass_obj
@authenticated
def list(obj, app_name: str, n: int) -> None:
    '''List all jobs related to an app'''
    click.echo(f"Listing all {app_name}'s jobs...\n")

    api = AiCloudApi(token=obj.get("access_token"))
    res = api.list_jobs(app_name=app_name, size=n)
    data = res.json()
    
    jobs = data['data']
    if len(jobs) > 0:
        table = PrettyTable(['ID', 'Status', 'Created at'])
        for job in jobs:
            table.add_row([job['id'], job['status'], job['createdAt']])
        click.echo(table)
    else:
        click.echo('This app has no job')
