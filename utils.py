from datetime import datetime

from data.auth import Session
from data.user import Login


def is_session_valid(session: Session):
    if session.expires_at < datetime.now():
        return False
    return True


def is_email_or_username(string: str) -> Login:
    return Login.EMAIL if '@' in string else Login.USERNAME
