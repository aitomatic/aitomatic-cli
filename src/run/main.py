import click
import json
from pathlib import Path


@click.command()
def run():
    '''Run the app based on config file'''
    config_data = read_aito_file()
    click.echo(config_data)


def read_aito_file():
    current_dir = Path.cwd()
    config_files = list(current_dir.glob('.aito'))
    if len(config_files) == 0:
        click.echo(
            'There is no .aito config file in current folder. Please create one first'
        )
        exit(1)

    try:
        return json.loads(config_files[0].read_text())
    except json.decoder.JSONDecodeError:
        click.echo("Can't read config file")
        exit(1)
