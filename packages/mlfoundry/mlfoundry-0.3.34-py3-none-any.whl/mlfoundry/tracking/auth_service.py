from mlflow.utils.rest_utils import MlflowHostCreds, http_request_safe

from mlfoundry.tracking.entities import AuthServerInfo


class AuthService:
    def __init__(self, auth_server_info: AuthServerInfo):
        self.host_creds = MlflowHostCreds(host=auth_server_info.auth_server_url)

    def get_token(self, api_key: str) -> str:
        response = http_request_safe(
            host_creds=self.host_creds,
            endpoint="/api/v1/oauth/api-keys/token",
            method="post",
            json={"apiKey": api_key},
        )
        response = response.json()
        token = response["accessToken"]
        return token
