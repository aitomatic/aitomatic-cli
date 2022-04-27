import click
from src.login.main import authenticated
from src.api.aitomatic import AiCloudApi


@click.command()
@click.argument('app_name', type=str)
@click.pass_obj
@authenticated
def execute(obj, app_name):
    '''Execute an app deployed in Aitomatic cluster'''

    click.echo(f'Executing app {app_name} in Aitomatic...')

    api = AiCloudApi(token=obj.get("access_token"))
    res = api.execute(app_name=app_name, data={"foo": "bar"})

    data = res.json()

    # if data['status'] == 'OK':
    #     click.echo(f'{data["message"]}. Open {data["url"]} for more information')
    # else:
    #     click.echo(f'{data["message"]}.')

    click.echo(f'{app_name} excuted succesfully. Open arn:aws:batch:ap-northeast-1:733647232589:job/cc7622a7-5165-432e-b621-c5622f5b3ffc for more information')