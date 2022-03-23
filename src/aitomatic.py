import click
from src.app.deploy import deploy


@click.group()
def aitomatic_cli():
    pass


@aitomatic_cli.command()
def hello():
    click.echo('Welcome to Aitomatic CLI!')


@aitomatic_cli.group()
def app():
    pass

app.add_command(deploy)

if __name__ == '__main__':
    aitomatic_cli()
