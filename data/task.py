from datetime import datetime

from pydantic import BaseModel, field_validator


class TaskUpdate(BaseModel):
    id: int
    name: str | None = None
    description: str | None = None
    alert_date_time: datetime | None = None

    @property
    def alert_date_str(self) -> str:
        return self.alert_date_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


class TaskCreate(BaseModel):
    name: str
    description: str | None = None
    done: bool = False
    alert_date_time: datetime | None = None
    user_id: int

    @field_validator('alert_date_time')
    def validate_alert_date_time(cls, value):
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        return None

    @field_validator('done')
    def validate_done(cls, value):
        return bool(value)

    @property
    def alert_date_str(self) -> str:
        return self.alert_date_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


class Task(BaseModel):
    id: int
    name: str
    description: str | None = None
    done: bool
    alert_date_time: datetime | None = None

    @field_validator('alert_date_time')
    def validate_alert_date_time(cls, value):
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')[:-3]
        return None

    @field_validator('done')
    def validate_done(cls, value):
        return bool(value)

    @property
    def alert_date_str(self) -> str:
        return self.alert_date_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


class TaskInDb(Task):
    user_id: int
