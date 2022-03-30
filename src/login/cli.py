import click
import requests
import time


ORG = 'aitomaticinc.us.auth0.com';
CLIENT_ID = "zk9AB0KtNqJY0gVeF1p0ZmUb2tlcXpYq"
AUDIENCE = "https://apps.aitomatic.com/dev"
SCOPE = "openid profile email"

@click.command(help='''
    Login to Aitomatic cloud
''')
def login():
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

def polling_authentication(device_info):
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

    polling_data = res.json();

    if polling_data['error'] == 'authorization_pending':
        time.sleep(device_info['interval'])
        polling_authentication(device_info)

    if polling_data['error'] == 'expired_token':
        click.echo(polling_data['error_description'])
        exit(1)


    