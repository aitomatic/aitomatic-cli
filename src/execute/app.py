import click
from src.login.main import authenticated
from src.api.aitomatic import AiCloudApi
from src.utils import show_error_message


@click.command()
@click.argument('app_name', type=str)
@click.pass_obj
@authenticated
def app(obj, app_name):
    '''Execute an app deployed in Aitomatic cluster'''

    click.echo(f'Executing app {app_name} in Aitomatic...')

    data = execute_app(app_name=app_name, data={'foo': 'bar'})
    if data['status'] == 'success':
        click.echo(f'{data["message"]}. Open {data["url"]} for more information')
    else:
        show_error_message(f'{data["message"]}.')


@click.pass_obj
def execute_app(obj, app_name, data):
    api = AiCloudApi(token=obj.get("access_token"))
    res = api.execute(app_name=app_name, data=data)

    data = res.json()
    return data
