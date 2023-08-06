from typing import Optional

from fastapi import HTTPException
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from jose import jwt

security = HTTPBearer()


class JWTTokenParser:

    async def get_payload_by_access_token(self,
                                          key: str,
                                          algorithm: Optional[str] = "HS256",
                                          credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
        """
        token payload = {"sub": user_id, "role": "backoffice", "exp": datetime, "scope": "access_token"}
        """
        current_access_token = credentials.credentials
        try:
            payload = jwt.decode(
                current_access_token,
                key,
                algorithms=[algorithm],
            )
            if payload.get('scope') == 'access_token':
                return payload
            raise HTTPException(status_code=401, detail='Invalid scope for token')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Access token expired')
        except jwt.JWTError as e:
            raise HTTPException(status_code=401, detail=str(e))