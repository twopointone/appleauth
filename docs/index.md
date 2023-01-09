# Apple Auth

__Version:__ 0.0.1

Python library to implement Sign In with Apple in your Django backend.

### 🍎 Apple docs

From now on, some stuff is much better explained on the Apple docs, so when in doubt just check (if you haven't done so) the following documents:

- [Sign In With Apple](https://developer.apple.com/sign-in-with-apple/get-started/)
- [Request an authorization to the Sign in with Apple server](https://developer.apple.com/documentation/sign_in_with_apple/request_an_authorization_to_the_sign_in_with_apple_server)
- [Generate and validate tokens](https://developer.apple.com/documentation/sign_in_with_apple/generate_and_validate_tokens)
- [Revoke tokens](https://developer.apple.com/documentation/sign_in_with_apple/revoke_tokens)

### 📝 Configuration

To start using the lib, some Apple Keys needs to be generated:

...

### 🚀 Usage

You can install the library directly from PYPI using pip:

```bash
pip install appleauth
```

Edit your settings.py file and update `INSTALLED_APPS` and `APPLE_CONFIG`:

```python
INSTALLED_APPS = [
        ...,
        "appleauth"
]

# Apple Config
APPLE_CONFIG = {
    "APPLE_KEY_ID": "",
    "APPLE_TEAM_ID": "",
    "APPLE_CLIENT_ID": "",
    "APPLE_PRIVATE_KEY": "",
    "APPLE_REDIRECT_URL": "",
    "APPLE_SCOPE": ["name", "email"],
    "TOKEN_CALLBACK_URL": "",
    "RESPONSE_HANDLER_CLASS": "",
}
```

Create Response Handler Class and update path in `APPLE_CONFIG`:

```python
from appleauth.services import AppleAuthResponseHandler

class AppleSignInResponseHandler(AppleAuthResponseHandler):
    def handle_fetch_or_create_user(self, request, user_dict):
        email = user_dict.get("email", None)
        apple_id = user_dict.get("apple_id", None)

        # Implement a method to handle user creation
        user = get_or_create_user(email, apple_id)

        return user

    def generate_response_json(self, user, extra_context):

        # Implement a serializer to serialize user data
        response = AuthUserSerializer(user, context=extra_context)

        return response.data
```

Update Routes:

```python
from rest_framework.routers import DefaultRouter
from appleauth.apis import AppleAuthViewset

default_router = DefaultRouter(trailing_slash=False)

default_router.register("auth/apple", AppleAuthViewset, basename="apple-auth")
```

NOTE:

- `AuthUserSerializer` used in above ref. could be created as per app's functionality and contain fields which needs to be sent in response of authorization.
- `get_or_create_user` method used in above code ref. could be created as per app's functionality.

### 🤖 Endpoints

- Provides following APIs:
    - [**Authorization URL API**](endpoints/#get-authorization-url)
        - It generates Apple's `authorization-url` used to redirect to Apple's Authorization Server to request consent from resource owner.
    - [**Authorize API**](endpoints/#authorize-user)
        - Exchange authorization code for access token.
        - Talk to resource server with access token and fetch user's profile information.
    - [**Authorize IOS Token API**](endpoints/#authorize-ios-token)
        - Verifies an ID Token issued by Apple's authorization server.
        - Fetch user details from decoded token.

**NOTE:** This documentation changes frequently, checkout the [changelog](changelog.md) for detailed breaking changes and features added.

Write your documentation using **Markdown** in `docs/` folder. Need help? Read mkdocs [documentation][mkdocs].

[mkdocs]: http://www.mkdocs.org/user-guide/writing-your-docs/
