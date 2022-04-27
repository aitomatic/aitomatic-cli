import os
import requests


class AiCloudApi:
    def __init__(self, token):
        self.token = token
        self.API_BASE = os.getenv(
            'AI_CLI_API_BASE',
            'http://a20ae33fe805a4d24bef115a973c630a-434493144.us-west-2.elb.amazonaws.com',
        )

    def deploy(self, app_name, data):
        res = requests.post(
            url=f"{self.API_BASE}/app/{app_name}/deploy",
            data=data,
            headers={
                'content-type': 'application/x-www-form-urlencoded',
                'Authorization': f'Bearer {self.token}',
            },
        )

        return res

    def execute(self, app_name, data):
        res = requests.post(
            url=f"{self.API_BASE}/app/{app_name}/execute",
            data=data,
            headers={
                'content-type': 'application/x-www-form-urlencoded',
                'Authorization': f'Bearer {self.token}',
            },
        )

        return res
