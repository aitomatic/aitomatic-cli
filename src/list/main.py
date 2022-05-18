import click


@click.command()
@click.argument('app_name', type=str)
def list(app_name):
    '''List all jobs related to an app'''
    click.echo(f"Listing all {app_name}'s jobs...")
