import click


@click.command()
@click.argument('job_id', type=str)
def logs(job_id):
    '''Show log of a job'''
    click.echo(f'Retrieving log of job {job_id}')
