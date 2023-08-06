from datetime import datetime

from pydantic import BaseModel


class AccessToken(BaseModel):
    access_token: str
    refresh_token: str
    creation_time: datetime
    expires_in: int
    refresh_expires_in: int
