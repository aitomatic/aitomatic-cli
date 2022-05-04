import click
import json
from configparser import ConfigParser
from pathlib import Path
from src.login.main import authenticated
from src.execute.app import execute_app


@click.command()
@authenticated
def run():
    '''Run the app based on config file'''
    config_data = read_aito_file()

    app_name = config_data['name']
    app_config = {}
    if config_data.get('config') is not None:
        app_config = config_data['config']
    elif config_data.get('config_file') is not None:
        file_path = Path.cwd() / config_data['config_file']
        app_config = convert_ini_config_to_dict(file_path.read_text())
    click.echo(json.dumps(app_config))

    data = execute_app(app_name=app_name, data=json.dumps(app_config))
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


def convert_ini_config_to_dict(config_content):
    parser = ConfigParser()
    result = {}

    parser.read_string(config_content)
    for section in parser.sections():
        result[section] = {}
        for name, value in parser.items(section):
            result[section][name] = value

    return result
