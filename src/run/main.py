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
    aito_config = AitoConfig()

    data = execute_app(
        app_name=aito_config.app_name, data=json.dumps(aito_config.app_config)
    )
    click.echo(data)


class AitoConfig:
    def __init__(self) -> None:
        self.aito_config = self.read_aito_file()
        self.app_name = self.aito_config.get('name')
        if self.aito_config.get('config_file') is not None:
            try:
                file_path = Path.cwd() / self.aito_config['config_file']
                self.app_config = self.convert_ini_config_to_dict(file_path.read_text())
            except FileNotFoundError:
                click.echo("Can't load app config file")
                exit(1)
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
            click.echo("Can't read config file.")
            exit(1)

    def convert_ini_config_to_dict(self, config_content):
        parser = ConfigParser()
        result = {}

        parser.read_string(config_content)
        for section in parser.sections():
            result[section] = {}
            for name, value in parser.items(section):
                result[section][name] = value

        return result
