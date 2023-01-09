# Third Party Stuff
from rest_framework import serializers


class AppleAuthCodeSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)


class AppleAuthUrlSerializer(serializers.Serializer):
    auth_url = serializers.CharField(required=True)


class AppleIDTokenSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=True)


class AppleTokenSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    id_token = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    user = serializers.JSONField(required=False)
    error = serializers.CharField(required=False)
