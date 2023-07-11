import os
import json
import requests
from tqdm import tqdm
from aitomatic.dsl.arl_handler import ARLHandler
from aitomatic.objects.model import Model
from aitomatic.objects.dataset import Dataset
import time
import pandas as pd


MODEL_API_ROOT = {
    "local": "http://localhost:8000/",
    "dev": "https://model-api-dev.platform.aitomatic.com",
    "staging": "https://model-api-stg.platform.aitomatic.com",
    "production": "https://model-api-prod.platform.aitomatic.com",
}

CLIENT_API_ROOT = {
    "local": "http://localhost:8000/api/client",
    "dev": "https://dev.platform.aitomatic.com/api/client",
    "staging": "https://staging.platform.aitomatic.com/api/client",
    "production": "https://production.platform.aitomatic.com/api/client",
}


def get_api_root(aitomatic_environment=None):
    if aitomatic_environment is None:
        aitomatic_environment = os.getenv("AITOMATIC_ENVIRONMENT")

    model_api_root = MODEL_API_ROOT.get(aitomatic_environment)
    client_api_root = CLIENT_API_ROOT.get(aitomatic_environment)
    return model_api_root, client_api_root


def get_project_id(project_name: str, api_token: str = None):
    if api_token is None:
        api_token = os.getenv("AITOMATIC_API_TOKEN")

    _, api_root = get_api_root()
    url = f"{api_root}/project"
    headers = {
        "authorization": api_token,
        "Content-Type": "application/json",
        "accept": "application/json",
    }
    data = {"project_name": project_name}
    resp = requests.post(url, headers=headers, json=data)
    # Handle request errors
    if resp.status_code != 200:
        err = f"{resp.status_code}: {resp.content}"
        raise ConnectionError(err)

    resp_content = json.loads(resp.content)
    id_ = resp_content["id"]
    return id_


class ProjectManager:
    def __init__(self, project_name: str = None, api_token: str = None):
        if api_token is None:
            api_token = os.getenv("AITOMATIC_API_TOKEN")

        if project_name is None:
            project_name = os.getenv("AITOMATIC_PROJECT_NAME")
            project_id = os.getenv("AITOMATIC_PROJECT_ID")
        else:
            project_id = get_project_id(project_name, api_token=api_token)

        self.project_name = project_name
        self.project_id = project_id
        self.api_token = api_token
        self.headers = {
            "accept": "application/json",
            "authorization": api_token,
            "Content-Type": "application/json",
        }
        self.init_endpoints()

    def init_endpoints(self):
        _, self.API_ROOT = get_api_root()
        self.KNOWLEDGE_LIST = f"{self.API_ROOT}/{self.project_id}/knowledges"
        self.KNOWLEDGE_DETAIL = lambda id_: f"{self.API_ROOT}/knowledges/" + id_
        self.MODELS_LIST = f"{self.API_ROOT}/{self.project_id}/models"
        self.MODEL_DETAIL = lambda id_: f"{self.API_ROOT}/models/" + id_
        self.MODEL_DELETE = f"{self.API_ROOT}/models/delete"
        self.MODEL_BUILD = f"{self.API_ROOT}/models"
        self.DATA_LIST = f"{self.API_ROOT}/{self.project_id}/data"
        self.DATA_DETAIL = lambda id_: f"{self.API_ROOT}/data/" + id_
        self.DATA_UPLOAD = f"{self.API_ROOT}/data/upload"
        self.BULK_MODEL_DETAIL = f"{self.API_ROOT}/models/status"
        self.RUN_INFERENCES = f"{self.API_ROOT}/inference"
        self.BULK_INFERENCE_DETAIL = f"{self.API_ROOT}/inference/status"
        self.DOWNLOAD_INFERENCE = (
            lambda id_: f"{self.API_ROOT}/inference/{id_}/download"
        )

    def get_model_list(self):
        resp = self.make_request("get", self.MODELS_LIST)
        if resp:
            models = []
            for m in resp:
                models.append(Model(m))
            return models

    def get_model_info(self, model_name: str):
        id_ = self.get_model_id(model_name)
        resp = self.make_request("get", self.MODEL_DETAIL(id_))
        if resp:
            model = Model(resp)
            return model

    def get_model_id(self, model_name: str):
        model_list = self.make_request("get", self.MODELS_LIST)
        id_ = [x["id"] for x in model_list if x["name"].lower() == model_name.lower()]
        if len(id_) == 0:
            raise ValueError(f"model {model_name} not found.")

        return id_[0]

    def get_data_info(self, data_name: str):
        id_ = self.get_data_id(data_name)
        resp = self.make_request("get", self.DATA_DETAIL(id_))
        if resp:
            return Dataset(resp)

    def get_data_id(self, data_name: str):
        data_list = self.make_request("get", self.DATA_LIST)
        id_ = [x["id"] for x in data_list if x["name"].lower() == data_name.lower()]
        if len(id_) == 0:
            raise ValueError(f"Dataset {data_name} not found.")

        return id_[0]

    def make_request(self, request_type: str, url: str, headers=None, **kwargs):
        if headers is None:
            headers = self.headers

        return make_request(request_type, url, headers=headers, **kwargs)

    def get_knowledge_info(self, knowledge_set_name: str) -> dict:
        id_ = self.get_knowledge_id(knowledge_set_name)
        data = make_request("get", self.KNOWLEDGE_DETAIL(id_), headers=self.headers)
        return data

    def get_knowledge(self, knowledge_set_name: str) -> ARLHandler:
        knowledge = self.get_knowledge_info(knowledge_set_name)["structured"]
        return ARLHandler(knowledge)

    def get_knowledge_id(self, knowledge_set_name: str):
        knowledges = make_request("get", self.KNOWLEDGE_LIST, headers=self.headers)
        id_ = [
            x["id"]
            for x in knowledges
            if x["name"].lower() == knowledge_set_name.lower()
        ]
        if len(id_) == 0:
            raise ValueError(f"knowledge set {knowledge_set_name} not found.")

        return id_[0]

    # TODO: Move to model builder class

    def get_base_conclusion_mapping(self, knowledge: ARLHandler):
        return {k: None for k in knowledge.conclusions.get("conclusions", {}).keys()}

    def get_base_metadata(self, dataset: Dataset, model: Model):
        schema_mapping = model.schema_mapping

        result = {}
        dataset_metadata = dataset.metadata
        for key in schema_mapping:
            if dataset_metadata.get(schema_mapping.get(key)):
                result[key] = dataset_metadata.get(schema_mapping.get(key))

        return result

    def delete_model_by_model_name(self, model_name):
        data = {"project": self.project_name, "model_name": model_name}
        self.headers["Accept-Language"] = "en-US,en;q=0.9,vi;q=0.8,es;q=0.7"
        make_request("post", self.MODEL_DELETE, headers=self.headers, json=data)

    def delete_models(self, model_names):
        for model_name in tqdm(model_names):
            self.delete_model_by_model_name(model_name)

    def upload_data(self, dataset_name: str, file_name: str, file):
        data = {
            "project_name": self.project_name,
            "dataset_name": dataset_name,
        }
        make_request(
            "post",
            self.DATA_UPLOAD,
            headers={
                "accept": "application/json",
                "authorization": self.api_token,
            },
            data=data,
            files={"file": (file_name, file, "application/parquet")},
        )

    def get_model_status_bulk(self, ids):
        data = {"ids": ids}
        resp = make_request(
            "post",
            self.BULK_MODEL_DETAIL,
            headers={
                "accept": "application/json",
                "authorization": self.api_token,
            },
            json=data,
        )
        status = []
        output = []
        for x in resp:
            status.append(x["status"].lower())
            output.append(x["output"] if x["output"] else None)
        return status, output

    def run_inference(self, model_name: list, dataset_name: str):
        data = {
            "model_name": model_name,
            "dataset_name": dataset_name,
            "project_name": self.project_name,
        }

        resp = make_request(
            "post",
            self.RUN_INFERENCES,
            headers={
                "accept": "application/json",
                "authorization": self.api_token,
            },
            json=data,
        )

        return resp

    def get_inference_status_bulk(self, ids):
        data = {"ids": ids}
        resp = make_request(
            "post",
            self.BULK_INFERENCE_DETAIL,
            headers={
                "accept": "application/json",
                "authorization": self.api_token,
            },
            json=data,
        )
        status = []
        for x in resp.get("results", []):
            status.append(x["status"].lower())
        return status

    def wait_for_inference_to_complete(self, file_path: str, sleep_time: int = 10):
        print("Waiting for inference jobs to complete")
        model_df = pd.read_parquet(file_path)
        while True:
            not_done_df: pd.DataFrame = model_df[
                (model_df["status"] != "success") & (model_df["status"] != "error")
            ]
            ids = not_done_df["id"].to_list()

            # call request to bulk get model info
            status = self.get_inference_status_bulk(ids)

            not_done_df.loc[:, "status"] = status

            model_df.update(not_done_df)

            success_length = len(model_df[model_df["status"] == "success"])
            error_length = len(model_df[model_df["status"] == "error"])
            df_length = len(model_df)
            print(
                f"Waiting for inference jobs to complete: [{success_length} success, {error_length} error, {df_length} total]"
            )
            # print(f"MODEL_DF: {model_df.to_string()}")
            model_df.to_parquet(file_path)
            if model_df["status"].isin(["running"]).any():
                time.sleep(sleep_time)
            else:
                break
        return model_df

    def download_inference_file(self, id: str, file_path: str):
        url = self.DOWNLOAD_INFERENCE(id)
        resp = requests.post(
            url,
            headers={
                "authorization": self.api_token,
            },
        )
        with open(file_path, "wb") as f:
            f.write(resp.content)

    def download_inference_results(self, folder_path: str, df: pd.DataFrame):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for index, row in df.iterrows():
            if row["status"] == "success":
                id = row["id"]
                file_name = row["file_name"]
                file_path = os.path.join(folder_path, file_name)
                self.download_inference_file(id, file_path)


def make_request(request_type: str, url: str, **kwargs):
    func = getattr(requests, request_type)
    if func is None:
        raise ValueError(
            f"Invalid request type {request_type}. " f"Must be get, post or put"
        )

    resp = func(url, **kwargs)
    # Handle request errors
    if resp.status_code != 200:
        err = f"{resp.status_code}: {resp.content}"
        raise ConnectionError(err)

    resp_content = json.loads(resp.content)
    return resp_content
