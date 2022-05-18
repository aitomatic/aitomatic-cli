import click
from src.api.aitomatic import AiCloudApi


@click.command()
@click.argument('app_name', type=str)
@click.option('-n', 'n', default=10, help='Number of jobs')
@click.pass_obj
def list(obj, app_name: str, n: int) -> None:
    '''List all jobs related to an app'''
    click.echo(f"Listing all {app_name}'s jobs...")

    api = AiCloudApi(token=obj.get("access_token"))
    res = api.list_jobs(app_name=app_name)
    data = res.json()
    
    jobs = data['jobs']
    if len(jobs) > 0:
        click.secho('ID     Status      Created at', fg='green')
        for job in jobs:
            click.echo(f"{job['id']}        {job['status']}     {job['createdAt']}")
    else:
        click.echo('This app has no job')
