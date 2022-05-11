import click
from pathlib import Path
from src.login.main import authenticated
from src.execute.app import execute_app
from src.utils import read_ini_file, show_error_message
from src.constants import AITOMATIC_PROFILE


@click.command()
@click.option(
    '-c',
    '--config',
    'app_config_file',
    type=click.STRING,
    help='ini file to run the app',
)
@authenticated
def run(app_config_file):
    '''Run the app based on .aito config file'''
    aito_config = AitoConfig()
    if app_config_file is not None:
        aito_config.set_app_config(app_config_file)

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
            show_error_message(
                'No .aito file in current folder. Please create one first.'
            )
            exit(1)

        try:
            return read_ini_file(config_files[0])[AITOMATIC_PROFILE]
        except KeyError:
            show_error_message(f"Can't read .aito config file")
            exit(1)

    def set_app_config(self, app_config_file):
        try:
            file_path = Path.cwd().joinpath(app_config_file)
            self.app_config = read_ini_file(file_path)
        except FileNotFoundError:
            show_error_message("Can't read app config file")
            exit(1)
