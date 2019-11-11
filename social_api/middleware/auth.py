from starlette.authentication import (
    AuthenticationBackend,
    AuthenticationError,
    AuthCredentials,
    BaseUser,
)
import jwt
from social_api import config
from social_api.models.user import USER_COLLECTION
import logging


class CustomAuthenticatedUser(object):
    def __init__(self, id: str, username: str) -> None:
        self.id: str = id
        self.username: str = username

    @property
    def is_authenticated(self) -> bool:
        return True


class AuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        auth = request.headers.get("Authorization", None)
        if auth:
            # authorization in form of: "JWT sjjkjuhdshduiui"
            scheme, credentials = auth.split(" ")
            if scheme.lower() != "jwt":
                return
            try:
                decoded = jwt.decode(
                    credentials, config.get("SECRET", default=""), algorithms=["HS256"],
                )
            except jwt.PyJWTError as e:
                # raise Exception(f"Exception decoding token: {e}")
                logging.info(f"error decoding authorization: {e}")
                return
            """
                decoded has form of: {"username": value, \
                "password": hashed_password, id: value, expire: datetime}
            """
            if not all([bool(decoded.get(key, None)) for key in ["username", "password", "id", "expire"]]):
                raise AuthenticationError("Invalid token.")
            else:
                # get 1 user object from database with id
                user = USER_COLLECTION.document(
                    u"{}".format(decoded["id"])
                ).get()
                # check user existence:
                if user.exists:
                    userData = user.to_dict()
                    if decoded["password"] == userData.get("password"):
                        return (
                            AuthCredentials(["authenticated"]),
                            CustomAuthenticatedUser(
                                id=decoded["id"],
                                username=decoded["username"]
                            ),
                        )
                    return
                else:
                    return
        else:
            return
