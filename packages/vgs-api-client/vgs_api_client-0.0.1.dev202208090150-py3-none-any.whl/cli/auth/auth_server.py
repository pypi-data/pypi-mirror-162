import os
import threading


from cli.auth import auth_api
from cli.auth.auth_utils import code_challenge, generate_code_verifier
from sdk.api.utils import is_port_accessible
from cli.auth.keyring_token_util import KeyringTokenUtil
from cli.auth.callback_server import RequestServer
from cli.auth.token_handler import CodeHandler


class AuthServer:
    env_url = {
        "dev": "https://auth.verygoodsecurity.io",
        "prod": "https://auth.verygoodsecurity.com",
    }
    token_util = KeyringTokenUtil()
    token_handler = CodeHandler()

    # Api
    CLIENT_ID = "vgs-cli-public"
    SCOPES = "idp openid"
    AUTH_URL = "{base_url}/auth/realms/vgs/protocol/openid-connect/auth"
    CALLBACK_PATH = "/callback"

    # AuthZ
    code_verifier = generate_code_verifier()
    code_method = "S256"
    oauth_access_token = None

    # Server constants.
    # Ports have been chosen based on Unassigned port list: https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml?&page=111
    ports = [7745, 8390, 9056]
    host = os.getenv("AUTH_SERVER_BIND_IP", "127.0.0.1")
    accessible_port = None
    app = None

    def __init__(self, environment):
        self.accessible_port = next(
            port for port in self.ports if is_port_accessible(self.host, port)
        )
        self.app = RequestServer(self.host, self.accessible_port)
        self.environment = environment
        self.auth_api = auth_api.create_api(environment)

    def refresh_authentication(self):
        self.token_util.put_tokens(auth_api.refresh_token(self.auth_api).body)

    def retrieve_access_token(self):
        callback_url = self.__get_host() + self.CALLBACK_PATH
        response = auth_api.get_token(
            self.auth_api, self.token_handler.get_code(), self.code_verifier, callback_url
        )
        self.set_access_token(response.body)

    def set_access_token(self, token):
        self.token_util.put_tokens(token)

    def __get_host(self):
        return "http://" + self.host + ":" + str(self.accessible_port)

    def client_credentials_login(self, client_id, secret):
        response = auth_api.get_auto_token(self.auth_api, client_id=client_id, client_secret=secret)
        self.set_access_token(response.body)

    class ServerThread(threading.Thread):
        def __init__(self, app):
            self.app = app
            threading.Thread.__init__(self)

        def run(self):
            self.app.run()
