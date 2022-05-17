import json
import os
import requests


class AiCloudApi:
    def __init__(self, token):
        self.token = token
        self.API_BASE = os.getenv(
            'AI_CLI_API_BASE',
            'https://koda.dev.cloud.aitomatic.com',
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

    def trigger(self, app_name, data):
        processed_data = {'config': data}
        res = requests.post(
            url=f"{self.API_BASE}/app/{app_name}/start",
            data=json.dumps(processed_data),
            headers={
                'content-type': 'application/json',
                'Authorization': f'Bearer {self.token}',
            },
        )

        return res
