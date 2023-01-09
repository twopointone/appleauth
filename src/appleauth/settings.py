# Third Party Stuff
from django.conf import settings
from django.test.signals import setting_changed
from django.utils.module_loading import import_string

DEFAULTS = {
    "RESPONSE_HANDLER_CLASS": "",
    "FE_REDIRECT_URL_PARAM": "fe_redirect_url",
    "APPLE_KEY_ID": "",
    "APPLE_TEAM_ID": "",
    "APPLE_CLIENT_ID": "",
    "APPLE_PRIVATE_KEY": "",
    "APPLE_REDIRECT_URL": "",
    "TOKEN_CALLBACK_URL": "",
    "APPLE_AUTHORIZATION_URL": "https://appleid.apple.com/auth/authorize",
    "APPLE_ACCESS_TOKEN_URL": "https://appleid.apple.com/auth/token",
    "APPLE_VALIDATION_URL": "https://appleid.apple.com",
    "APPLE_TOKEN_TTL": 60 * 60 * 24 * 180,
    "APPLE_SCOPE": ["name", "email"],
}

IMPORT_STRINGS = [
    "RESPONSE_HANDLER_CLASS",
]


def perform_import(val, setting_name):
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    return val


def import_from_string(val, setting_name):
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import '%s' for Apple API setting '%s'. %s: %s." % (
            val,
            setting_name,
            e.__class__.__name__,
            e,
        )
        raise ImportError(msg)


class AppleAPISettings:
    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "APPLE_CONFIG", {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid Apple API setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


apple_api_settings = AppleAPISettings(None, DEFAULTS, IMPORT_STRINGS)


def reload_apple_api_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == "APPLE_CONFIG":
        apple_api_settings.reload()


setting_changed.connect(reload_apple_api_settings)
