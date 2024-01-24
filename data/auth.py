from datetime import datetime

from pydantic import BaseModel, field_validator


class SessionCreate(BaseModel):
    token: str
    user_id: int
    expires_at: datetime

    @field_validator('expires_at')
    def validate_expires_at(cls, value):
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        raise ValueError('expires_at must be datetime or a string in the format "YYYY-MM-DD HH:MM:SS.SSS"')

    @property
    def expires_at_str(self) -> str:
        return self.expires_at.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


class Session(BaseModel):
    id: int
    token: str
    user_id: int
    expires_at: datetime

    @field_validator('expires_at')
    def validate_expires_at(cls, value):
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        raise ValueError('expires_at must be datetime or a string in the format "YYYY-MM-DD HH:MM:SS.SSS"')

    @property
    def expires_at_str(self) -> str:
        return self.expires_at.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


class Token(BaseModel):
    access_token: str
    token_type: str
