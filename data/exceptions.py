class UserAlreadyExistsException(Exception):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message if message else "User already exists")


class UserWithUsernameAlreadyExistsException(UserAlreadyExistsException):
    def __init__(self, username: str):
        super().__init__(f'User with username {username} already exists')


class UserWithEmailAlreadyExistsException(UserAlreadyExistsException):
    def __init__(self, email: str):
        super().__init__(f'User with email {email} already exists')


class UserNotFoundException(Exception):
    def __init__(self, user_data_type: str, user_data: str):
        super().__init__(f'User with {user_data_type} {user_data} does not exist')


class SessionNotFoundException(Exception):
    def __init__(self, token: str):
        super().__init__(f'Session with token {token} does not exist')


class TaskNotFoundException(Exception):
    def __init__(self, task_id: str):
        super().__init__(f'Task with id {task_id} does not exist')
