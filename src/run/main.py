import click
import json
from pathlib import Path
from src.login.main import authenticated
from src.execute.app import execute_app


@click.command()
@authenticated
def run():
    '''Run the app based on config file'''
    config_data = read_aito_file()
    app_name = config_data['name']
    data = execute_app(app_name=app_name, data={'foo': 'bar'})
    click.echo(config_data)
    click.echo(data)


def read_aito_file():
    current_dir = Path.cwd()
    config_files = list(current_dir.glob('.aito'))
    if len(config_files) == 0:
        click.echo(
            'There is no .aito config file in current folder. Please create one first.'
        )
        exit(1)

    try:
        return json.loads(config_files[0].read_text())
    except json.decoder.JSONDecodeError:
        click.echo("Can't read config file.")
        exit(1)
