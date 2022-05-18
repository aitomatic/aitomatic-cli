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
    click.echo(f'Running app {app_name}...\n')

    current_dir = Path.cwd() if app_path is None else Path.cwd().joinpath(app_path)
    config = aito_confg['app'].get('config')
    data = {}
    if ctx.params['app_config_file'] is not None:
        data = read_ini_file(Path.cwd().joinpath(ctx.params['app_config_file']))
    elif config is not None:
        data = read_ini_file(current_dir.joinpath(config))

    res = start_app(app_name=app_name, data=data)
    if res['status'] == 'success':
        click.echo('App started successfully')
        click.secho(f"Run `aito logs {res['job_id']}` to view job's log", fg='green')
    else:
        show_error_message('App failed to start')


def read_aito_file(folder_path: Path) -> dict:
    aito_file_path = folder_path.joinpath('.aito')
    result = read_ini_file(aito_file_path)
    if not is_valid_aito_file(result):
        show_error_message('.aito file is not valid')
        exit(1)
    return result


def is_valid_aito_file(aito_obj: dict) -> bool:
    if 'project' in aito_obj or 'app' in aito_obj:
        return True
    return False


@click.pass_obj
def start_app(obj, app_name: str, data: dict) -> dict:
    api = AiCloudApi(token=obj.get("access_token"))
    res = api.start_app(app_name=app_name, data=data)

    data = res.json()
    return data
