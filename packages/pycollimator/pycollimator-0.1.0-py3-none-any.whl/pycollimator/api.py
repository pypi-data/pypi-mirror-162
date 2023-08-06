import typing as T
import requests
from uuid import uuid4

from pycollimator.i18n import N
from pycollimator.log import Log
from pycollimator.error import CollimatorAuthenticationError, CollimatorApiError, CollimatorRetryableApiError
from pycollimator.global_variables import GlobalVariables


class Api:
    BASE_PATH = "/api/v0"

    @classmethod
    def _handle_error(cls, response: T.Any, headers: T.Dict[str, str] = None):
        request_id = (headers is not None) and headers.get("X-Request-ID") or None
        # correlation_id = headers and headers.get('X-Correlation-ID') or None
        if response.status_code >= 400:
            if response.status_code == 401:
                Log.debug("API error 401, response:", response.text)
                raise CollimatorAuthenticationError(
                    N("Authentication failed. Please check your token or reload the page.")
                )
            elif response.status_code == 504:
                Log.trace("API error 504, retrying...")
                raise CollimatorRetryableApiError
            else:
                Log.debug("API error, status_code:", response.status_code, "response:", response.text)
                raise CollimatorApiError(
                    f"API call failed (status: {response.status_code}). Support request ID: "
                    + f"{request_id}. Detailed error:\n{response.text}"
                )

    # TODO add streaming support for logs and results
    @classmethod
    def _call_api(
        cls, api, method, body: T.Any = None, headers: dict = None, body_type="json", response_type="json", retries=3
    ):
        try:
            url = GlobalVariables.url() + api
            headers = headers or GlobalVariables.custom_headers()
            headers["X-Collimator-API-Caller"] = "python-notebook"
            headers["X-Request-ID"] = str(uuid4())
            if body is None:
                Log.trace(method, url)
                response = requests.request(method, url, headers=headers)
            elif body_type == "json":
                Log.trace(method, url, body)
                headers["Content-Type"] = "application/json"
                response = requests.request(method, url, json=body, headers=headers)
            elif body_type == "files":
                Log.trace(method, url, body)
                response = requests.request(method, url, files=body, headers=headers)
            cls._handle_error(response, headers)
            Log.trace(method, "response:", response.text)
            if response_type == "text":
                return response.text
            return response.json()
        except CollimatorRetryableApiError as e:
            if retries > 0:
                Log.trace(method, "retrying...")
                return cls._call_api(api, method, body, headers, body_type, response_type, retries - 1)
            raise e

    @classmethod
    def get(cls, api):
        return cls._call_api(api, method="GET")

    @classmethod
    def post(cls, api, body):
        return cls._call_api(api, method="POST", body=body)

    @classmethod
    def put(cls, api, body):
        return cls._call_api(api, method="PUT", body=body)

    @classmethod
    def delete(cls, api, body):
        return cls._call_api(api, method="DELETE", body=body)

    @classmethod
    def get_projects(cls):
        api = f"{Api.BASE_PATH}/projects"
        return cls.get(api)

    @classmethod
    def get_project(cls, project_uuid: str = None) -> dict:
        project_uuid = project_uuid or GlobalVariables.project_uuid()
        api = f"{Api.BASE_PATH}/projects/{project_uuid}"
        return cls.get(api)

    @classmethod
    def get_model(cls, model_uuid: str) -> dict:
        api = f"{Api.BASE_PATH}/models/{model_uuid}"
        return cls.get(api)

    @classmethod
    def simulation_create(cls, model_uuid: str, body: dict) -> dict:
        api = f"{Api.BASE_PATH}/models/{model_uuid}/simulations"
        return cls.post(api, body)

    @classmethod
    def simulation_get(cls, model_uuid: str, simulation_uuid: str) -> dict:
        api = f"{Api.BASE_PATH}/models/{model_uuid}/simulations/{simulation_uuid}"
        return cls.get(api)

    @classmethod
    def simulation_start(cls, model_uuid: str, simulation_uuid: str) -> dict:
        api = f"{Api.BASE_PATH}/models/{model_uuid}/simulations/{simulation_uuid}/start"
        return cls.post(api, None)

    @classmethod
    def simulation_parameters_set(cls, model_uuid: str, simulation_uuid: str, body: dict) -> dict:
        api = f"{Api.BASE_PATH}/models/{model_uuid}/simulations/{simulation_uuid}/parameters"
        return cls.put(api, body)

    @classmethod
    def simulation_hashed_file_create(cls, model_uuid: str, simulation_uuid: str, body: dict) -> dict:
        api = f"{Api.BASE_PATH}/models/{model_uuid}/simulations/{simulation_uuid}/hashed_files"
        return cls.post(api, body)

    @classmethod
    def simulation_hashed_file_upload(cls, path: str, upload_url: str) -> dict:
        with open(path, "rb") as file:
            return cls._call_api(upload_url, method="PUT", body={"file": file}, body_type="files")

    # FIXME should be a stream
    @classmethod
    def simulation_logs(cls, model_uuid: str, simulation_uuid: str) -> str:
        api = f"{Api.BASE_PATH}/models/{model_uuid}/simulations/{simulation_uuid}/logs"
        return cls._call_api(api, method="GET", response_type="text")

    # FIXME should be a stream
    @classmethod
    def simulation_results(cls, model_uuid: str, simulation_uuid: str) -> str:
        api = f"{Api.BASE_PATH}/models/{model_uuid}/simulations/{simulation_uuid}/csv_results"
        return cls._call_api(api, method="GET", response_type="text")

    @classmethod
    def model_configuration_update(cls, model_uuid: str, body: dict) -> dict:
        api = f"{Api.BASE_PATH}/models/{model_uuid}/configuration"
        return cls.put(api, body)

    @classmethod
    def linearization_results_csv(cls, model_uuid: str, simulation_uuid: str) -> str:
        api = f"{Api.BASE_PATH}/models/{model_uuid}/simulations/{simulation_uuid}/lin_results"
        return cls._call_api(api, method="GET", response_type="text")
