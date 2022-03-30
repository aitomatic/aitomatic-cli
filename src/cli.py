import click
from src.app.cli import app
from src.login.cli import login


@click.group(help='''
    Aitomatic CLI tool to help manage aitomatic projects and apps
''')
def cli():
    pass

cli.add_command(app)
cli.add_command(login)

if __name__ == '__main__':
    cli()
