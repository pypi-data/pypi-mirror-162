import json

import urllib3

from iqs_client.api_client import ApiClient
from iqs_client.configuration import Configuration


class ApiClientWithOIDC(ApiClient):

    def __init__(self, configuration: Configuration, token_path="/token"):
        super().__init__(configuration)
        self.token_path = token_path
        self.username = configuration.username
        configuration.username = None
        self.password = configuration.password
        configuration.password = None
        self._get_or_refresh_token()

    def _get_or_refresh_token(self, force_new=False):
        auth_url = self.configuration.host.replace("/api", "") + self.token_path
        if self.configuration.access_token:
            auth_req = {
                "accessToken": self.configuration.access_token
            }
        else:
            auth_req = {
                "username": self.username,
                "password": self.password,
                "forceNew": force_new
            }
        http = urllib3.PoolManager()
        response = http.request('POST', auth_url, body=json.dumps(auth_req).encode('utf-8'))
        if 200 <= response.status < 300:
            try:
                token = json.loads(response.data.decode('utf-8'))
                self.configuration.access_token = token['token']
            except json.JSONDecodeError as error:
                raise Exception("Response isn't token.", f"{error.msg} For: {error.doc}")
        else:
            raise Exception(f"Response status: {response.status}", f"Body: {response.data.decode('utf-8')}")

    def call_api(self, resource_path, method,
                 path_params=None, query_params=None, header_params=None,
                 body=None, post_params=None, files=None,
                 response_type=None, auth_settings=None, async_req=None,
                 _return_http_data_only=None, collection_formats=None,
                 _preload_content=True, _request_timeout=None, _host=None):
        self._get_or_refresh_token()
        return super().call_api(resource_path, method,
                                path_params=path_params, query_params=query_params,
                                header_params=header_params,
                                body=body, post_params=post_params, files=files,
                                response_type=response_type, auth_settings=auth_settings,
                                async_req=async_req,
                                _return_http_data_only=_return_http_data_only,
                                collection_formats=collection_formats,
                                _preload_content=_preload_content,
                                _request_timeout=_request_timeout, _host=_host)
