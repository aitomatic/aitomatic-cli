import click


@click.group()
def aitomatic_cli():
    pass

@aitomatic_cli.command()
def hello():
    click.echo('Welcome to Aitomatic CLI!')

if __name__ == '__main__':
    aitomatic_cli()
