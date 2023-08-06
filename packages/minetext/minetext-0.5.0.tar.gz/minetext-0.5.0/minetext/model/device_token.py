from pydantic import BaseModel


class DeviceToken(BaseModel):
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
