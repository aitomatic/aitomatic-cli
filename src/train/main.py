import click

@click.command()
def train():
    '''CLI to train models'''
    click.echo('Checking configuration file ...')
    click.echo('Detected k-swe ... checking parameters')
    click.echo('Create training job with name: crazy-fox-2022-04-25-werwre')
    click.echo(
        'Succesfully registered job crazy-fox-2022-04-25-werwre in Aitomatic cloud'
    )