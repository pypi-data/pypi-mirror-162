from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .hyperbloq_jwt import HyperbloqJWT, HyperbloqJWTError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class VerifyAccessToken:
    def __init__(
      self,
      pub_key: str = None,
      aud: List = None,
      alg: List = ['RS256'],
      decode_user=True,
    ):
        self.jwt = HyperbloqJWT(pub_key, aud, alg)

    def __call__(self, token: str = Depends(oauth2_scheme)):
        try:
            self.jwt.verify_access_token(token)
            if self.decode_user:
              return self.jwt.get_current_user()
            
            return self.jwt.get_decoded_token()

        except HyperbloqJWTError as e:
          raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
          )

        except Exception as e:
          raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
          )
