import click
from pathlib import Path
from src.api.aitomatic import AiCloudApi
from src.login.main import authenticated
from src.utils import read_ini_file, show_error_message


@click.command()
@click.option(
    '-c',
    '--config',
    'app_config_file',
    type=click.STRING,
    help='ini file to run the app',
)
@authenticated
def run(app_config_file: str) -> None:
    '''Run the app based on .aito config file'''
    aito_config = read_aito_file(Path.cwd())
    if 'project' in aito_config.keys():
        run_project(aito_config)
    else:
        run_app(aito_config)


def run_project(aito_config: dict) -> None:
    project_name = aito_config['project']['name']
    apps = []
    for key in aito_config.keys():
        if 'app' in key:
            apps.append({'name': key.split(' ')[1], 'src': aito_config[key]['src']})
    if len(apps) == 0:
        click.echo(f'Project {project_name} has no app to run')
        exit(0)
    elif len(apps) == 1:
        selected_app = apps[0]
    else:
        click.echo(f'Project {project_name} has {len(apps)} apps. Please select one.')
        for i in range(len(apps)):
            click.secho(
                f'Select {i + 1} to run app {apps[i]["name"]}.', fg='green', bold=True
            )
        choice = click.prompt(
            'Please select app to run',
            type=click.Choice([str(i) for i in range(1, len(apps) + 1)]),
        )
        selected_app = apps[int(choice) - 1]

    app_path = Path.cwd().joinpath(selected_app['src'])
    app_aito_config = read_aito_file(app_path)
    run_app(app_aito_config, app_path)


@click.pass_context
def run_app(ctx, aito_confg: dict, app_path: Path = None) -> None:
    app_name = aito_confg['app']['name']
    click.echo(f'Running app {app_name}...')

    current_dir = Path.cwd() if app_path is None else Path.cwd().joinpath(app_path)
    config = aito_confg['app'].get('config')
    data = {}
    if ctx.params['app_config_file'] is not None:
        data = read_ini_file(Path.cwd().joinpath(ctx.params['app_config_file']))
    elif config is not None:
        data = read_ini_file(current_dir.joinpath(config))
    
    click.echo(data)
    res = trigger_app(app_name=app_name, data=data)
    click.echo(res)


def read_aito_file(folder_path: Path) -> dict:
    files = list(folder_path.glob('.aito'))

    if len(files) == 0:
        show_error_message('.aito file not found. Please create one first.')
        exit(1)

    try:
        result = read_ini_file(files[0])
        if not is_valid_aito_file(result):
            show_error_message(f".aito file is not valid")
            exit(1)
        return result
    except KeyError:
        show_error_message(f"Can't read .aito config file")
        exit(1)


def is_valid_aito_file(aito_obj: dict) -> bool:
    if 'project' in aito_obj or 'app' in aito_obj:
        return True
    return False


@click.pass_obj
def trigger_app(obj, app_name: str, data: dict) -> dict:
    api = AiCloudApi(token=obj.get("access_token"))
    res = api.trigger(app_name=app_name, data=data)

    data = res.json()
    return data
