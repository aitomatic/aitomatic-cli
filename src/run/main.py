import click
import json
from pathlib import Path
from src.login.main import authenticated
from src.execute.app import execute_app
from src.utils import read_ini_file


@click.command()
@click.option(
    '-c',
    '--config',
    'config_file',
    type=click.STRING,
    help='ini file to run the app',
)
@authenticated
def run(config_file):
    '''Run the app based on .aito config file'''
    aito_config = AitoConfig()
    if config_file is not None:
        aito_config.set_app_config(config_file)

    data = execute_app(app_name=aito_config.app_name, data=aito_config.app_config)
    click.echo(data)


class AitoConfig:
    def __init__(self) -> None:
        self.aito_config = self.read_aito_file()
        self.app_name = self.aito_config.get('name')
        if self.aito_config.get('config_file') is not None:
            self.set_app_config(self.aito_config['config_file'])
        else:
            self.app_config = {}

    def read_aito_file(self):
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
            click.echo("Can't read .aito config file.")
            exit(1)

    def set_app_config(self, app_config_file):
        try:
            file_path = Path.cwd().joinpath(app_config_file)
            self.app_config = read_ini_file(file_path)
        except FileNotFoundError:
            click.echo("Can't read app config file")
            exit(1)
