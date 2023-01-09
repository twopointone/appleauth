# Standard Library
import json
from urllib.parse import quote, urlencode

# Third Party Stuff
from django.http import HttpResponseRedirect
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Apple Auth Stuff
from appleauth.mixins import MultipleSerializerMixin
from appleauth.serializers import (
    AppleAuthCodeSerializer,
    AppleIDTokenSerializer,
    AppleTokenSerializer,
)
from appleauth.services import AppleAuth
from appleauth.settings import apple_api_settings


class AppleAuthViewset(MultipleSerializerMixin, viewsets.GenericViewSet):
    response_handler_class = apple_api_settings.RESPONSE_HANDLER_CLASS
    permission_classes = [AllowAny]
    serializer_classes = {
        "authorize": AppleAuthCodeSerializer,
        "authorize_ios": AppleIDTokenSerializer,
        "token": AppleTokenSerializer,
    }

    @action(methods=["GET"], detail=False, url_path="auth-url")
    def auth_url(self, request, *args, **kwargs):
        # Fetch Query Params
        extra_state = request.GET.get("state", None)
        redirect_url = request.GET.get("redirect_url", None)

        # Retrieve state and auth params
        apple_auth = AppleAuth()
        state = apple_auth.get_state(redirect_url, extra_state)
        auth_params = apple_auth.get_auth_params(state)

        authorization_url = (
            f"{apple_api_settings.APPLE_AUTHORIZATION_URL}?{auth_params}"
        )
        return Response({"authorization_url": authorization_url})

    @action(methods=["POST"], detail=False, url_path="authorize")
    def authorize(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response_handler = self.response_handler_class()
        code = serializer.validated_data["code"]
        apple_auth = AppleAuth(code=code, response_handler=response_handler)

        user_dict = apple_auth.do_auth()
        user, context = apple_auth.get_user_details(request, user_dict)
        response_dict = response_handler.generate_response_json(user, context)

        return Response(response_dict)

    @action(methods=["POST"], detail=False, url_path="authorize/ios")
    def authorize_ios(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response_handler = self.response_handler_class()
        id_token = serializer.validated_data["id_token"]

        apple_auth = AppleAuth(response_handler=response_handler)
        user_dict = apple_auth.ios_auth(id_token)

        user, context = apple_auth.get_user_details(request, user_dict)
        response_dict = response_handler.generate_response_json(user, context)

        return Response(response_dict)

    @action(methods=["POST"], detail=False, url_path="token")
    def token(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = {
            "code": serializer.validated_data.get("code"),
            "state": serializer.validated_data.get("state"),
            "error": serializer.validated_data.get("error"),
        }

        try:
            state_json = json.loads(serializer.validated_data.get("state"))
            redirect_url = state_json[AppleAuth.FE_REDIRECT_URL_PARAM]
            params = urlencode(data, quote_via=quote)
        except Exception:
            redirect_url = apple_api_settings.TOKEN_CALLBACK_URL
            params = json.dumps({"error": "state_not_found"})

        url = f"{redirect_url}?{params}"
        return HttpResponseRedirect(redirect_to=url)
