from typing import List
from jwt import decode, ExpiredSignatureError

from .models import User


class HyperbloqJWTError(Exception):
    """Exception raised for errors in the jwt decode.

    Attributes:
        message -- explanation of the error
    """

    def __init__(
      self,
      message="Missing params for decoding jwt 'pub_key' and 'aud' are required",
    ):
        self.message = message
        super().__init__(self.message)


class HyperbloqJWT:
    def __init__(self, pub_key: str = None, aud: List = None, alg: List = ["RS256"]):
        if not pub_key or not aud or not alg:
            raise HyperbloqJWTError

        self.secret = f"-----BEGIN PUBLIC KEY-----\r\n{pub_key}\r\n-----END PUBLIC KEY-----"
        self.audience = aud
        self.algorithms = alg
        self.decoded_token = {}

    def verify_access_token(self, token):
        try:
            payload = decode(
                token,
                self.secret,
                audience=self.audience,
                algorithms=self.algorithms,
                options={
                  "verify_signature": True,
                  "verify_aud": True,
                  "verify_exp": True,
                },
            )
            self.decoded_token = payload
            return payload

        except ExpiredSignatureError:
            raise HyperbloqJWTError(message="Could not verify token")
    
    def get_current_user(self):
        data = self.decoded_token
        if not data:
            raise HyperbloqJWTError(message="Could not decode token")

        return User(**{
          "username": data.get("preferred_username"),
          "userId": data.get("sub"),
          "profileId": data.get("profile"),
          "name": data.get("name"),
          "given_name": data.get("given_name"),
          "family_name": data.get("family_name"),
          "email": data.get("email"),
          "locale": data.get("locale"),
          "resources": data.get("resource_access"),
          "email_verified": data.get("email_verified")
        })
    
    def get_decoded_token(self):
        if not self.decoded_token:
            raise HyperbloqJWTError(message="Could not decode token")

        return self.decoded_token
