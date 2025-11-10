from typing import Optional, Tuple

import jwt
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from .models import User


class SimpleJWTAuthentication(BaseAuthentication):
    """
    Lightweight JWT authentication that validates tokens issued by our manual
    login endpoint.
    """

    keyword = "Bearer"

    def authenticate(self, request) -> Optional[Tuple[User, str]]:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2:
            raise exceptions.AuthenticationFailed(
                _("Invalid Authorization header format.")
            )

        keyword, token = parts
        if keyword.lower() != self.keyword.lower():
            return None

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
        except jwt.ExpiredSignatureError as exc:
            raise exceptions.AuthenticationFailed(_("Token has expired.")) from exc
        except jwt.InvalidTokenError as exc:
            raise exceptions.AuthenticationFailed(_("Invalid token.")) from exc

        user_id = payload.get("user_id")
        if not user_id:
            raise exceptions.AuthenticationFailed(_("Token contained no user id."))

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed(_("User not found.")) from exc

        return user, token

