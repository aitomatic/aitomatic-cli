import click
from configparser import ConfigParser
import requests
from multiprocessing import Process, Queue
from http.server import HTTPServer
import time
from functools import update_wrapper, partial

from .server import LoginServer
from src.utils import (
    get_random_string,
    create_code_challenger,
    create_code_verifier,
    show_error_message,
)
from src.constants import CREDENTIAL_FILE, AITOMATIC_PROFILE
from src.logout.main import remove_local_credential_file

ORG = 'aitomaticinc.us.auth0.com'
CLIENT_ID = 'zk9AB0KtNqJY0gVeF1p0ZmUb2tlcXpYq'
AUDIENCE = 'https://apps.aitomatic.com/dev'
SCOPE = 'openid profile email offline_access'
PORT = 56921


@click.command()
@click.pass_obj
def login(obj):
    '''Login to Aitomatic cloud'''
    if CREDENTIAL_FILE.exists():
        re_login = click.confirm(
            "You're logged in. Do you want to log in again?",
            default=False,
            abort=False,
            prompt_suffix=': ',
            show_default=True,
            err=False,
        )

        if not re_login:
            exit(0)

    do_login()


@click.pass_obj
def do_login(obj):
    code_verifier = create_code_verifier()
    code_challenge = create_code_challenger(code_verifier)
    obj['code_challenge'] = code_challenge
    obj['code_verifier'] = code_verifier
    obj['login_seed'] = get_random_string(50)

    # start server to handle login callback from auth0
    start_server()

    # start the authentication flow
    initiate_login_flow()

    # wait for the login callback
    wait_for_login_callback()


@click.pass_obj
def start_server(obj):
    service = None
    message_queue = Queue()  # share state between processes
    obj['message_queue'] = message_queue

    try:
        service = Process(
            name='login_server',
            target=setup_server,
            args=(
                message_queue,
                obj,
                '0.0.0.0',
                PORT,
            ),
        )
        service.daemon = True
        service.start()
    except KeyboardInterrupt:
        service.join()
        exit(0)


# set up webserver to handle login callback from auth0
def setup_server(obj, exchange_code, hostName, serverPort):
    handler = partial(LoginServer, obj, exchange_code)
    webServer = HTTPServer((hostName, serverPort), handler)

    try:
        webServer.serve_forever()
        return webServer
    except KeyboardInterrupt:
        webServer.server_close()
        exit(0)


@click.pass_obj
def initiate_login_flow(obj):
    code_challenge = obj.get('code_challenge')
    login_seed = obj.get('login_seed')

    url = (
        f'https://{ORG}/authorize'
        f'?response_type=code'
        f'&code_challenge_method=S256'
        f'&code_challenge={code_challenge}'
        f'&client_id={CLIENT_ID}'
        f'&redirect_uri=http://localhost:{PORT}'
        f'&scope={SCOPE}'
        f'&audience={AUDIENCE}'
        f'&state={login_seed}'
        f'&max_age=3600'
    )

    click.launch(url)


@click.pass_obj
def wait_for_login_callback(obj):
    try:
        code = obj['message_queue'].get()

        if code is not None:
            res = requests.post(
                url='https://{}/oauth/token'.format(ORG),
                data={
                    'client_id': CLIENT_ID,
                    'grant_type': 'authorization_code',
                    'code_verifier': obj['code_verifier'],
                    'code': code,
                    'redirect_uri': f'http://localhost:{PORT}',
                },
                headers={'content-type': 'application/x-www-form-urlencoded'},
            )

            # response example
            # {'error': 'authorization_pending', 'error_description': 'User has yet to authorize device code.'}
            # {'error': 'expired_token', 'error_description': '...' }
            # {'error': 'access_denied', 'error_description': '...' }
            # {'access_token': '...', 'id_token': '...', 'refresh_token': '...'}
            polling_data = res.json()

            if polling_data.get('access_token') is not None:
                save_credential(
                    access_token=polling_data['access_token'],
                    refresh_token=polling_data.get('refresh_token', ''),
                    id_token=polling_data.get('id_token', ''),
                )
                click.echo('Login successfully')
                exit(0)
            return

        time.sleep(5)
        wait_for_login_callback()
    except KeyboardInterrupt:
        show_error_message('Login flow interrupted by user')
        exit(1)


@click.pass_obj
def save_credential(obj, access_token, refresh_token, id_token):
    obj['access_token'] = access_token
    obj['refresh_token'] = refresh_token
    obj['id_token'] = id_token

    parser = ConfigParser()
    parser[AITOMATIC_PROFILE] = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'id_token': id_token,
    }

    if not CREDENTIAL_FILE.exists():
        CREDENTIAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CREDENTIAL_FILE, 'w') as f:
        parser.write(f)


def authenticated(f):
    @click.pass_obj
    def wrapper(obj, *args, **kwargs):
        token = obj.get('access_token')

        if token is None or len(token) == 0:
            prompt_login()

        res = requests.get(
            url='https://{}/userinfo'.format(ORG),
            headers={'Authorization': 'Bearer {}'.format(token)},
        )

        if res.status_code == 200:
            f(*args, **kwargs)
        elif res.status_code == 401:
            refresh_token()
            f(*args, **kwargs)
        else:
            prompt_login()

    return update_wrapper(wrapper, f)


def prompt_login():
    show_error_message("You're not logged in. Please run `aito login` first.")
    remove_local_credential_file()
    exit(1)


@click.pass_obj
def refresh_token(obj):
    token = obj.get('refresh_token')

    if token is None or len(token) == 0:
        prompt_login()

    res = requests.post(
        url='https://{}/oauth/token'.format(ORG),
        data={
            'client_id': CLIENT_ID,
            'grant_type': 'refresh_token',
            'refresh_token': obj['refresh_token'],
        },
        headers={'content-type': 'application/x-www-form-urlencoded'},
    )
    if res.status_code == 200:
        data = res.json()
        save_credential(
            access_token=data['access_token'],
            refresh_token=token,
            id_token=data.get('id_token', ''),
        )
    else:
        prompt_login()
