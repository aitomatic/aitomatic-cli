import click
import requests
import time
import json
from pathlib import Path
from functools import update_wrapper

ORG = 'aitomaticinc.us.auth0.com';
CLIENT_ID = "zk9AB0KtNqJY0gVeF1p0ZmUb2tlcXpYq"
AUDIENCE = "https://apps.aitomatic.com/dev"
SCOPE = "openid profile email offline_access"
CONFIG_FILE = Path.home().joinpath('.aitomatic')

def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    else:
        return None

AUTH_INFO = load_config()

@click.command(help='''
    Login to Aitomatic cloud
''')
@click.pass_obj
def login(obj):
    if (obj is not None and obj.get("at") is not None) or CONFIG_FILE.exists():
        relogin = click.confirm("You're logged in. Do you want to log in again?", default=False, abort=False, prompt_suffix=': ', show_default=True, err=False)

        if not relogin:
            exit(0)

    do_login()

def do_login():
    click.echo('Login to Aitomatic cloud')
    device_info = request_device_code()
    display_device_info(device_info)
    polling_authentication(device_info)

def request_device_code():
    res = requests.post(
        url="https://{}/oauth/device/code".format(ORG),
        data={"client_id": CLIENT_ID, "scope": SCOPE, "audience": AUDIENCE},
        headers={ "content-type": "application/x-www-form-urlencoded" }
    )

    # see details https://auth0.com/docs/get-started/authentication-and-authorization-flow/call-your-api-using-the-device-authorization-flow#request-device-code
    # print(device_response)
    # {
    #     'device_code': 'kJ3fIJ90RYXbdAOlhns3v7t3', 
    #     'user_code': '873280791', 
    #     'verification_uri': 'https://aitomaticinc.us.auth0.com/activate', 
    #     'expires_in': 900, 
    #     'interval': 5, 
    #     'verification_uri_complete': 'https://aitomaticinc.us.auth0.com/activate?user_code=873280791'
    # }

    return res.json()

def display_device_info(device_info):
    code = device_info['user_code']
    url = device_info['verification_uri_complete']

    click.echo("""
    Please visit the following URL:
    {}
    to login to Aitomatic cloud.

    Verification code: {}
    """.format(url, code))

    click.launch(url)

    click.echo("Waiting for authentication...")

@click.pass_obj
def polling_authentication(obj, device_info):
    res = requests.post(
        url="https://{}/oauth/token".format(ORG),
        data={
            "client_id": CLIENT_ID, 
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code", 
            "device_code": device_info['device_code']
        },
        headers={ "content-type": "application/x-www-form-urlencoded" }
    )
    
    # response example
    # {'error': 'authorization_pending', 'error_description': 'User has yet to authorize device code.'}
    # {"error": "expired_token", "error_description": "..." }
    # {"error": "access_denied", "error_description": "..." }
    # {"access_token": "...", "id_token": "...", "refresh_token": "..."}
    polling_data = res.json();

    if polling_data.get('error') == 'authorization_pending':
        time.sleep(device_info['interval'])
        polling_authentication(device_info)

    if polling_data.get('error') == 'expired_token' or polling_data.get('error') == 'access_denied':
        click.echo(polling_data['error_description'])
        exit(1)

    if polling_data.get('access_token') is not None:
        obj['at'] = polling_data['access_token']
        obj['rt'] = polling_data['refresh_token']
        save_config({ 'at': polling_data['access_token'], 'rt': polling_data['refresh_token'], 'id': polling_data['id_token'] })
        click.echo("Login successful!")

def save_config(data):
    CONFIG_FILE.write_text(json.dumps(data))

def authenticated(f):
    @click.pass_obj
    def wrapper(obj, *args, **kwargs):
        token = obj and obj.get("at")

        if token is None:
            prompt_login()
            exit(1)

        res = requests.get(
            url="https://{}/userinfo".format(ORG),
            headers={ "Authorization": "Bearer {}".format(token) }
        )

        if (res.status_code == 200):
            f(*args, **kwargs)
        else:
            prompt_login()
            exit(1)

    return update_wrapper(wrapper, f)

def prompt_login():
    click.echo("You're not logged in. Please run `aitomatic login` first.")
    
