import click
from src.app.cli import app


@click.group(help='''
    Aitomatic CLI tool to help manage aitomatic projects and apps
''')
def cli():
    pass

cli.add_command(app)

if __name__ == '__main__':
    cli()
