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

    def start_app(self, app_name, data):
        processed_data = {'input': data}
        res = requests.post(
            url=f"{self.API_BASE}/app/{app_name}/start",
            data=json.dumps(processed_data),
            headers={
                'content-type': 'application/json',
                'Authorization': f'Bearer {self.token}',
            },
        )

        return res

    def list_jobs(self, app_name, size):
        res = requests.get(
            url=f"{self.API_BASE}/app/{app_name}/jobs?size={size}",
            headers={
                'Authorization': f'Bearer {self.token}',
            },
        )
        return res

    def log_job(self, job_id):
        res = requests.get(
            url=f"{self.API_BASE}/job/{job_id}",
            headers={
                'Authorization': f'Bearer {self.token}',
            },
        )
        return res
