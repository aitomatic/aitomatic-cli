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
    
    # if app_config_file is not None:
    #     aito_config.set_app_config(app_config_file)

    # data = trigger_app(app_name=aito_config.app_name, data=aito_config.app_config)
    # click.echo(data)


def run_project(aito_config: dict) -> None:
    project_name = aito_config['project']['name']
    apps = []
    for key in aito_config.keys():
        if 'app' in key:
            apps.append({
                'name': key.split(' ')[1],
                'src': aito_config[key]['src']
            })
    if len(apps) == 0:
        click.echo(f'Project {project_name} has no app to run')
        exit(0)
    elif len(apps) == 1:
        selected_app = apps[0]
    else:
        click.echo(f'Project {project_name} has {len(apps)} apps. Please select one.')
        for i in range(len(apps)):
            click.secho(f'Select {i + 1} to run app {apps[i]["name"]}.', fg='green', bold=True)
        choice = click.prompt(
            'Please select app to run',
            type=click.Choice([str(i + 1) for i in range(len(apps))])
        )
        selected_app = apps[int(choice) - 1]

    app_path = Path.cwd().joinpath(selected_app['src'])
    app_aito_config = read_aito_file(app_path)
    run_app(app_aito_config)


def run_app(aito_confg: dict) -> None:
    click.echo(f'Running app {aito_confg["app"]["name"]}...')


def read_aito_file(folder_path: Path) -> dict:
    files = list(folder_path.glob('.aito'))
    
    if len(files) == 0:
        show_error_message(
            '.aito file not found. Please create one first.'
        )
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
