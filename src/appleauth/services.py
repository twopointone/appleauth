# Standard Library
import json
import time
from urllib.parse import quote, urlencode

# Third Party Stuff
import jwt
import requests
from django.utils.crypto import get_random_string

# Apple Auth Stuff
from appleauth.settings import apple_api_settings


class AppleAuthResponseHandler(object):
    def handle_fetch_or_create_user(self, request, user_dict):
        raise NotImplementedError()

    def generate_response_json(self, user, extra_context):
        raise NotImplementedError()


class AppleAuth(object):
    FE_REDIRECT_URL_PARAM = apple_api_settings.FE_REDIRECT_URL_PARAM
    RESPONSE_TYPE = "code"

    def __init__(self, code=None, response_handler=None):
        self.code = code
        self.response_handler = response_handler
        self.APPLE_ACCESS_TOKEN_URL = apple_api_settings.APPLE_ACCESS_TOKEN_URL

    def get_state(self, redirect_url, extra_state):
        identifier = get_random_string(128)
        state = {
            "identifier": identifier,
            self.FE_REDIRECT_URL_PARAM: redirect_url,
        }

        if extra_state:
            extra_state = json.loads(extra_state)
            state.update(extra_state)

        state = json.dumps(state)
        return state

    def get_auth_params(self, state=None):
        scope = apple_api_settings.APPLE_SCOPE

        params = {
            "client_id": apple_api_settings.APPLE_CLIENT_ID,
            "redirect_uri": apple_api_settings.APPLE_REDIRECT_URL,
        }

        # Update state
        if state:
            params["state"] = state

        # Update scope
        if scope:
            params["scope"] = " ".join(scope)

        # Update "response_type"
        if self.RESPONSE_TYPE:
            params["response_type"] = self.RESPONSE_TYPE

        # Update "response_mode"
        params["response_mode"] = "form_post"

        params = urlencode(params, quote_via=quote)
        return params

    def do_auth(self):
        response_data = {}
        client_id, client_secret = self.get_client_id_and_secret()
        headers = {"content-type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": self.code,
            "grant_type": "authorization_code",
        }
        apple_response = requests.post(
            self.APPLE_ACCESS_TOKEN_URL, data=data, headers=headers
        )
        response_dict = apple_response.json()
        id_token = response_dict.get("id_token", None)
        if id_token:
            decoded = jwt.decode(id_token, "secret", verify=False)
            response_data.update(
                {"email": decoded["email"]}
            ) if "email" in decoded else None
            response_data.update(
                {"apple_id": decoded["sub"]}
            ) if "sub" in decoded else None
        return response_data

    def get_user_details(self, request, response_dict):
        return self.response_handler.handle_fetch_or_create_user(request, response_dict)

    def get_client_id_and_secret(self):
        headers = {"kid": apple_api_settings.APPLE_KEY_ID}
        TOKEN_TTL = apple_api_settings.APPLE_TOKEN_TTL
        now = int(time.time())
        payload = {
            "iss": apple_api_settings.APPLE_TEAM_ID,
            "iat": now,
            "exp": now + TOKEN_TTL,
            "aud": apple_api_settings.APPLE_VALIDATION_URL,
            "sub": apple_api_settings.APPLE_CLIENT_ID,
        }

        client_secret = jwt.encode(
            payload,
            key=apple_api_settings.APPLE_PRIVATE_KEY,
            algorithm="ES256",
            headers=headers,
        ).decode("utf-8")

        return apple_api_settings.APPLE_CLIENT_ID, client_secret

    def ios_auth(self, id_token):
        response_data = {}
        if id_token:
            decoded = jwt.decode(id_token, "secret", verify=False)
            response_data.update(
                {"email": decoded["email"]}
            ) if "email" in decoded else None
            response_data.update(
                {"apple_id": decoded["sub"]}
            ) if "sub" in decoded else None
        return response_data
