import click
from src.login.main import authenticated
from src.api.aitomatic import AiCloudApi


@click.command()
@click.pass_obj
@authenticated
def execute(obj):
    '''Execute app in Aitomatic cluster'''

    click.echo('Execute furuno fixed-net train app in Aitomatic...')
    app_id = 'fish-finder'  # get the app id somehow

    api = AiCloudApi(token=obj.get("access_token"))
    res = api.execute(app_id=app_id, data={"foo": "bar"})

    click.echo('App executed successfully')
