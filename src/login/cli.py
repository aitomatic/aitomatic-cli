import click
import http.client
import requests


ORG = 'aitomaticinc.us.auth0.com';
CLIENT_ID = "zk9AB0KtNqJY0gVeF1p0ZmUb2tlcXpYq"
AUDIENCE = "https://apps.aitomatic.com/dev"
SCOPE = "openid profile email"

@click.command(help='''
    Login to Aitomatic cloud
''')
def login():
    click.echo('Login to Aitomatic cloud')

    conn = http.client.HTTPSConnection("")
    res = requests.post(
        url="https://{}/oauth/device/code".format(ORG),
        data={"client_id": CLIENT_ID, "scope": SCOPE, "audience": AUDIENCE},
        headers={ "content-type": "application/x-www-form-urlencoded" }
    )

    print(res.json())
    