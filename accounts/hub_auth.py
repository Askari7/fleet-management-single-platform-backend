"""
Hub JWT authentication for FleetManagement.

Allows tokens issued by the central hub (single-window-portal/hub) to
authenticate requests to this Django backend, so users logged in via the
portal don't need a separate FleetManagement account.

How it works:
  - The portal sends a JWT signed with HUB_JWT_SIGNING_KEY.
  - This class verifies that token and returns the matching local User,
    creating one on first login (linked by email).
  - If no hub token is present it returns None, falling through to the
    existing JWTAuthentication class (standalone mode still works).

Settings required in settings.py:
  HUB_JWT_SIGNING_KEY = 'same-value-as-hub/.env JWT_SIGNING_KEY'
  HUB_APP_SLUG = 'fleet'  # must match the slug created in hub admin
"""

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class HubJWTAuthentication(BaseAuthentication):
    def authenticate_header(self, request):
        return 'Bearer realm="fleet"'

    def authenticate(self, request):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return None

        token = header[len("Bearer "):]

        # Only handle tokens that carry the hub's 'apps' claim.
        # Tokens issued by this app's own simplejwt won't have it,
        # so they fall through to JWTAuthentication below.
        try:
            unverified = jwt.decode(token, options={"verify_signature": False})
        except jwt.DecodeError:
            return None

        if "apps" not in unverified:
            return None  # not a hub token, let simplejwt handle it

        try:
            payload = jwt.decode(
                token,
                settings.HUB_JWT_SIGNING_KEY,
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Hub token expired.")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid hub token.")

        email = payload.get("email")
        if not email:
            raise AuthenticationFailed("Hub token missing email claim.")

        app_slug = getattr(settings, "HUB_APP_SLUG", None)
        if app_slug and app_slug not in payload.get("apps", []):
            raise AuthenticationFailed("Access to Fleet Management not granted.")

        user = self._get_or_create_user(email, payload)
        return (user, token)

    def _get_or_create_user(self, email, payload):
        name = payload.get("name", "")
        parts = name.split(" ", 1)
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "first_name": parts[0],
                "last_name": parts[1] if len(parts) > 1 else "",
                "role": "contractor",
                "email_verified": True,
            },
        )
        return user
