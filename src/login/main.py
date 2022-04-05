import click
import requests
from multiprocessing import Process, Queue
from ctypes import c_wchar_p
from http.server import HTTPServer
from os import urandom
from base64 import urlsafe_b64encode
from hashlib import sha256
from re import sub
import time
import json
import random
import string
from pathlib import Path
from functools import update_wrapper, partial

from .server import LoginServer

ORG = "aitomaticinc.us.auth0.com"
CLIENT_ID = "zk9AB0KtNqJY0gVeF1p0ZmUb2tlcXpYq"
AUDIENCE = "https://apps.aitomatic.com/dev"
SCOPE = "openid profile email offline_access"
CREDENTIAL_FILE = Path.home().joinpath(".aitomatic/credentials")
PORT = 56921


@click.command()
@click.pass_obj
def login(obj):
    """Login to Aitomatic cloud"""
    if obj.get("access_token") is not None or CREDENTIAL_FILE.exists():
        re_login = click.confirm(
            "You're logged in. Do you want to log in again?",
            default=False,
            abort=False,
            prompt_suffix=": ",
            show_default=True,
            err=False,
        )

        if not re_login:
            exit(0)

    do_login()


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
def start_server(obj):
    service = None
    message_queue = Queue()  # share state between processes
    obj["message_queue"] = message_queue

    try:
        service = Process(
            name="login_server",
            target=setup_server,
            args=(
                message_queue,
                obj,
                "0.0.0.0",
                PORT,
            ),
        )
        service.daemon = True
        service.start()
    except KeyboardInterrupt:
        service.join()
        exit(0)


@click.pass_obj
def do_login(obj):
    code_verifier = create_code_verifier()
    code_challenge = create_code_challenger(code_verifier)
    obj["code_challenge"] = code_challenge
    obj["code_verifier"] = code_verifier
    obj["login_seed"] = get_random_string(50)

    # start server to handle login callback from auth0
    start_server()

    # start the authentication flow
    initiate_login_flow()

    # wait for the login callback
    wait_for_login_callback()


@click.pass_obj
def initiate_login_flow(obj):
    code_challenge = obj.get("code_challenge")
    login_seed = obj.get("login_seed")

    url = (
        f"https://{ORG}/authorize"
        f"?response_type=code"
        f"&code_challenge_method=S256"
        f"&code_challenge={code_challenge}"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri=http://localhost:{PORT}"
        f"&scope={SCOPE}"
        f"&audience={AUDIENCE}"
        f"&state={login_seed}"
    )

    click.launch(url)


@click.pass_obj
def wait_for_login_callback(obj):
    try:
        code = obj["message_queue"].get()

        if code is not None:
            res = requests.post(
                url="https://{}/oauth/token".format(ORG),
                data={
                    "client_id": CLIENT_ID,
                    "grant_type": "authorization_code",
                    "code_verifier": obj["code_verifier"],
                    "code": code,
                    "redirect_uri": f"http://localhost:{PORT}",
                },
                headers={"content-type": "application/x-www-form-urlencoded"},
            )

            # response example
            # {'error': 'authorization_pending', 'error_description': 'User has yet to authorize device code.'}
            # {"error": "expired_token", "error_description": "..." }
            # {"error": "access_denied", "error_description": "..." }
            # {"access_token": "...", "id_token": "...", "refresh_token": "..."}
            polling_data = res.json()

            if polling_data.get("access_token") is not None:
                save_credential(
                    {
                        "access_token": polling_data["access_token"],
                        "refresh_token": polling_data.get("refresh_token", ""),
                        "id": polling_data.get("id_token", ""),
                    }
                )
                click.echo("Login successful")
                exit(0)
            return

        time.sleep(5)
        wait_for_login_callback()
    except KeyboardInterrupt:
        print("Login flow interrupted by user")
        exit(1)


@click.pass_obj
def save_credential(obj, data):
    obj["access_token"] = data["access_token"]
    obj["refresh_token"] = data["refresh_token"]
    obj["id"] = data["id"]
    if not CREDENTIAL_FILE.exists():
        CREDENTIAL_FILE.parent.mkdir(parents=True)
    CREDENTIAL_FILE.write_text(json.dumps(data))


def authenticated(f):
    @click.pass_obj
    def wrapper(obj, *args, **kwargs):
        token = obj and obj.get("access_token")

        if token is None:
            prompt_login()
            exit(1)

        res = requests.get(
            url="https://{}/userinfo".format(ORG),
            headers={"Authorization": "Bearer {}".format(token)},
        )

        if res.status_code == 200:
            f(*args, **kwargs)
        else:
            prompt_login()
            exit(1)

    return update_wrapper(wrapper, f)


def prompt_login():
    click.echo("You're not logged in. Please run `aito login` first.")


def get_random_string(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def create_code_verifier():
    code_verifier = urlsafe_b64encode(urandom(40)).decode("utf-8")
    code_verifier = sub("[^a-zA-Z0-9]+", "", code_verifier)

    return code_verifier


def create_code_challenger(code_verifier):
    code_challenge = sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = urlsafe_b64encode(code_challenge).decode("utf-8")
    code_challenge = code_challenge.replace("=", "")
    return code_challenge
