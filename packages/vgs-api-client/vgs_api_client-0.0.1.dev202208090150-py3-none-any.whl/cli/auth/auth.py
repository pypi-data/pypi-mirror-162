from simple_rest_client.exceptions import ClientError

from cli.auth.auth_server import AuthServer
from sdk.api.errors import (
    AuthenticationError,
    AuthenticationRequiredError,
    TokenNotValidError,
    ClientCredentialsAuthenticationError,
)
from cli.auth.keyring_token_util import KeyringTokenUtil

token_util = KeyringTokenUtil()
TOKEN_FILE_NAME = "vgs_token"


def handshake(ctx, environment):
    try:
        if not token_util.validate_access_token():
            token_util.validate_refresh_token()
            AuthServer(environment).refresh_authentication()
    except ClientError as e:
        if e.response.body and e.response.body.get("error_description") == "Invalid refresh token":
            raise AuthenticationRequiredError(ctx)
        else:
            raise AuthenticationError(ctx, e.args[0])
    except TokenNotValidError:
        raise AuthenticationRequiredError(ctx)
    except Exception as e:
        raise AuthenticationError(ctx, e.args[0])


def client_credentials_login(ctx, client_id, client_secret, environment):
    try:
        if not token_util.is_access_token_valid() or token_util.is_access_token_azp_changed(
            client_id
        ):
            AuthServer(environment).client_credentials_login(client_id, client_secret)
    except (TokenNotValidError, ClientError):
        raise ClientCredentialsAuthenticationError(ctx)

    return True
