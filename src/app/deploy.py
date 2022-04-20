import json
import click
from src.login.main import authenticated
from src.api.aitomatic import AiCloudApi


@click.command()
@click.pass_obj
@authenticated
def deploy(obj):
    '''Deploy app to Aitomatic cluster'''

    click.echo('Deploy app to Aitomatic...')
    app_id = 'fish-finder'  # get the app id somehow

    api = AiCloudApi(token=obj.get("access_token"))
    res = api.deploy(app_id=app_id, data={"foo": "bar"})

    data = res.json()

    click.echo(f'App deployed successfully. Open {data["url"]}')

    # TODO launch the app in browser
    # click.launch(data["url"])

    # click.echo('User info', obj)
