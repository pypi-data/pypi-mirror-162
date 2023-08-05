import iqs_client
import iqs_api.api_decorator
from iqs_api.iqs_authentication import ApiClientWithOIDC


def connect(
        address: str = None,
        username: str = None,
        password: str = None,
        auth_header_name: str = None,
        auth_header_value: str = None,
        configuration=iqs_client.Configuration(),
        use_oidc: bool = False,

        token: str = None,
        auth_with_user_pw: bool = True,
        use_auth_header: bool = False
):
    configuration.host = address
    if configuration.access_token == "":
        configuration.access_token = None

    # Cases: Auth with password, auth with token, Session header/value
    # First priority: Session header
    if use_auth_header:
        # Disabling username, password and token, so ApiClient does not try to authenticate
        configuration.username = None
        configuration.password = None
        configuration.access_token = None

        setattr(configuration, 'auth_header_name', auth_header_name)
        setattr(configuration, 'auth_header_value', auth_header_value)

    elif auth_with_user_pw:
        configuration.username = username
        configuration.password = password
    else:
        configuration.access_token = token

    return IQSClient(configuration, use_oidc)


class IQSClient:
    def __init__(
            self,
            root_configuration,
            use_oicd
    ):
        if use_oicd:
            iqs_api.api_decorator.decorate_iqs_client(self, root_configuration, ApiClientWithOIDC)
        else:
            iqs_api.api_decorator.decorate_iqs_client(self, root_configuration, iqs_client.ApiClient)
