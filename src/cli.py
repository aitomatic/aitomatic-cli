import click
from src.app.deploy import deploy


@click.group(help='''
    Aitomatic CLI tool to help manage aitomatic projects and apps
''')
def cli():
    pass


@cli.group(help='''
    CLI sub-command to help manage aitomatic apps
''')
def app():
    pass

app.add_command(deploy)

if __name__ == '__main__':
    cli()
