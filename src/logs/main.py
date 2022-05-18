import click
from src.api.aitomatic import AiCloudApi
from src.utils import show_error_message


@click.command()
@click.argument('job_id', type=str)
@click.pass_obj
def logs(obj, job_id: str) -> None:
    '''Show log of a job'''
    click.echo(f'Retrieving log of job {job_id}...\n')

    api = AiCloudApi(token=obj.get("access_token"))
    res = api.log_job(job_id=job_id)
    data = res.json()
    if data['status'] != 'failure':
        click.echo(f"Job ID: {data['id']}")
        click.echo(f"Status: {data['status']}")
        click.echo(f"Created at: {data['createdAt']}")
        click.echo(f"Updated at: {data['updatedAt']}")
    else:
        show_error_message(data['message'])
