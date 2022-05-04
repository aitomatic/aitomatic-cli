import click
from pathlib import Path


@click.command()
def run():
    '''Run the app based on config file'''
    current_dir = Path.cwd()
    config_files = list(current_dir.glob('.aito'))
    if len(config_files) == 0:
        click.echo(
            'There is no .aito config file in current folder. Please create one first'
        )
        exit(1)
    click.echo(current_dir)
