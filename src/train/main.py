import click

@click.command()
def train():
    '''CLI to train k1st architecture'''
    click.echo('Checking configuration file ...')
    click.echo('Detected k-swe ... checking parameters')
    click.echo('Create training job with name: kswe-2022-04-25-werwre')
    click.echo(
        'Succesfully registered job kswe-2022-04-25-werwre in Aitomatic cloud'
    )