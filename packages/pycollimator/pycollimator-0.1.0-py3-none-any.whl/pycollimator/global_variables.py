import os
import re
import typing as T
import warnings

from pycollimator.i18n import N
from pycollimator.log import Log
from pycollimator.utils import is_uuid


class GlobalVariables:
    """
    global variables stores information about user's authentication and the project
    folder they are currently in
    """

    _instance: "GlobalVariables" = None
    _envRegex = re.compile("https://(dev|test|app).collimator.ai")

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(GlobalVariables, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if os.environ.get("CI") == "true":
            return
        self.set_auth_token(None)

    def set_auth_token(self, token: str, project: str = None, api_url: str = None) -> None:
        self.auth_token = token or self._detect_auth_token()
        self.project = project or self._detect_project()
        self.api_url = api_url or self._detect_api_url()
        Log.trace("auth_token:", self.auth_token, "project:", self.project, "api_url:", self.api_url)

    def _detect_auth_token(self) -> T.Optional[str]:
        if os.environ.get("AUTH_TOKEN") is not None:
            return os.environ["AUTH_TOKEN"]
        if os.path.isfile("token.txt"):
            with open("token.txt", "r") as token_file:
                return token_file.read().strip()
        warnings.warn(N("No token file found. Please call `collimator.set_auth_token()` to authenticate manually."))

    def _detect_project(self) -> str:
        if os.environ.get("PROJECT_UUID") is not None:
            return os.environ["PROJECT_UUID"]
        path = os.path.abspath(os.curdir)
        project_uuid = path.split("/")[-1]
        if not is_uuid(project_uuid):
            warnings.warn(N("Unable to detect the current project. API calls may fail."))
        return project_uuid

    def _detect_api_url(self) -> str:
        endpoint = None
        if os.environ.get("API_ENDPOINT") is not None:
            endpoint = os.environ["API_ENDPOINT"]
        elif os.path.isfile("environment.txt"):
            with open("environment.txt", "r") as environment_file:
                endpoint = environment_file.read().strip()
        if endpoint is not None:
            if endpoint.startswith("http://localhost"):
                return "http://localhost"
            if endpoint.startswith("http://host.docker.internal"):
                return "http://host.docker.internal"
            try:
                return GlobalVariables._envRegex.match(endpoint).group(0)
            except BaseException:
                warnings.warn(N("Unable to detect the environment, assuming https://app.collimator.ai."))
                return "https://app.collimator.ai"
        warnings.warn(N("Unable to detect the environment, assuming https://app.collimator.ai."))
        return "https://app.collimator.ai"

    @classmethod
    def _get_instance(cls) -> "GlobalVariables":
        if cls._instance is None:
            cls()
        return cls._instance

    @classmethod
    def project_uuid(cls):
        """
        stores the project uuid associated with the folder.
        """
        return cls._get_instance().project

    @classmethod
    def token(cls):
        """
        stores the authentication token
        """
        return cls._get_instance().auth_token

    @classmethod
    def url(cls):
        """
        stores the url, used for environment logic
        """
        return cls._get_instance().api_url

    @classmethod
    def custom_headers(cls) -> T.Dict[str, str]:
        """
        stores the authentication headers used in all API requests
        """
        # FIXME I think requests should be handling the content-type header for us
        custom_headers = {
            "X-Collimator-API-Token": cls._get_instance().auth_token,
            "Accept": "application/json",
            # "content-type": "application/json",
        }
        return custom_headers


def get_project_url() -> str:
    return GlobalVariables.url() + "/projects/" + GlobalVariables.project_uuid()


def set_auth_token(token: str, project_uuid: str = None, api_url: str = None) -> None:
    GlobalVariables._get_instance().set_auth_token(token, project_uuid, api_url)
