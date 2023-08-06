import os

from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from jose import jwt

load_dotenv()

security = HTTPBearer()


class JWTTokenParser:

    def __init__(self, secret_key=os.getenv("ACCESS_TOKEN_SECRET_KEY"), algorithm=os.getenv("ALGORITHM")):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def __call__(self, key: str = ""):
        if key:
            return self.secret_key in key
        return False

    async def get_payload_by_access_token(self,
                                          credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
        """
        token payload = {"sub": user_id, "role": "backoffice", "exp": datetime, "scope": "access_token"}
        """
        current_access_token = credentials.credentials
        try:
            payload = jwt.decode(
                current_access_token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            if payload.get('scope') == 'access_token':
                return payload
            raise HTTPException(status_code=401, detail='Invalid scope for token')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Access token expired')
        except jwt.JWTError as e:
            raise HTTPException(status_code=401, detail=str(e))

    async def get_current_user_id(
            self,
            credentials: HTTPAuthorizationCredentials = Security(security),
    ):
        current_access_token = credentials.credentials
        try:
            payload = jwt.decode(
                current_access_token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            if payload.get("sub"):
                return int(payload.get("sub"))
            raise HTTPException(status_code=401, detail='Access token expired')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Access token expired')
        except jwt.JWTError as e:
            raise HTTPException(status_code=401, detail=str(e))