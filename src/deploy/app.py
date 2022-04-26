import click
from src.login.main import authenticated
from src.api.aitomatic import AiCloudApi


@click.command()
@click.argument('app_name', type=str)
@click.pass_obj
@authenticated
def app(obj, app_name):
    '''Deploy app to Aitomatic cluster'''

    click.echo('Deploy app to Aitomatic...')

    api = AiCloudApi(token=obj.get("access_token"))
    res = api.deploy(app_id=app_name, data={"foo": "bar"})

    data = res.json()

    click.echo(f'App {app_name} deployed successfully. Open {data["url"]}')

    # TODO launch the app in browser
    # click.launch(data["url"])

    # click.echo('User info', obj)
