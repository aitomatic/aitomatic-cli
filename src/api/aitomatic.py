import os
import requests


class AiCloudApi:
    def __init__(self, token):
        self.token = token
        self.API_BASE = os.getenv(
            'AI_CLI_API_BASE',
            'http://a1adce51c15d34971924a8c7bb9feafd-904302004.us-west-2.elb.amazonaws.com',
        )

    def deploy(self, app_id, data):
        res = requests.post(
            url=f"{self.API_BASE}/app/{app_id}/deploy",
            data=data,
            headers={
                'content-type': 'application/x-www-form-urlencoded',
                'Authorization': f'Bearer {self.token}',
            },
        )

        return res
