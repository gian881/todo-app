import os
import sqlite3

from data.auth import SessionCreate, Session
from data.exceptions import UserNotFoundException, SessionNotFoundException, \
    TaskNotFoundException, UserWithUsernameAlreadyExistsException, UserWithEmailAlreadyExistsException
from data.task import TaskCreate, TaskUpdate, TaskInDb
from data.user import UserCreate, UserUpdate, UserInDb, User


class Database:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))

        self.conn = sqlite3.connect(os.path.join(script_dir, 'dev.sqlite'), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def create_user(self, user_to_create: UserCreate) -> None:
        try:
            self.cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                                (user_to_create.username, user_to_create.password, user_to_create.email))
            self.conn.commit()
        except sqlite3.IntegrityError as error:
            if 'username' in str(error):
                raise UserWithUsernameAlreadyExistsException(user_to_create.username)
            elif 'email' in str(error):
                raise UserWithUsernameAlreadyExistsException(user_to_create.email)

    def delete_user(self, user_id: int) -> None:
        self.cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        self.conn.commit()

    def update_user(self, user: UserUpdate) -> User:
        update_fields = []
        update_values = []

        if user.username is not None:
            update_fields.append('username = ?')
            update_values.append(user.username)
        if user.email is not None:
            update_fields.append('email = ?')
            update_values.append(user.email)
        if user.password is not None:
            update_fields.append('password = ?')
            update_values.append(user.password)

        if len(update_fields) == 0:
            raise ValueError('No fields to update')

        update_values.append(user.id)

        self.cursor.execute('SELECT * FROM users WHERE id = ?', (user.id,))
        user_found = self.cursor.fetchone()

        if not user_found:
            raise UserNotFoundException('id', str(user.id))

        try:
            self.cursor.execute(f'UPDATE users SET {", ".join(update_fields)} WHERE USERS.ID = ?', tuple(update_values))
            self.conn.commit()

            self.cursor.execute('SELECT * FROM users WHERE id = ?', (user.id,))
            user_updated = self.cursor.fetchone()

            if user_updated:
                return UserInDb(**user_updated)
            else:
                raise UserNotFoundException('id', str(user.id))
        except sqlite3.IntegrityError as error:
            if 'username' in str(error):
                raise UserWithUsernameAlreadyExistsException(user.username)
            elif 'email' in str(error):
                raise UserWithEmailAlreadyExistsException(user.email)

    def get_user_by_id(self, user_id: int) -> UserInDb:
        self.cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = self.cursor.fetchone()
        if user is None:
            raise UserNotFoundException('id', str(user_id))
        else:
            return UserInDb(**user)

    def get_user_by_email(self, email: str) -> UserInDb:
        self.cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = self.cursor.fetchone()
        if user is None:
            raise UserNotFoundException('email', email)
        return UserInDb(**user)

    def get_user_by_username(self, username: str) -> UserInDb:
        self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = self.cursor.fetchone()

        if user is None:
            raise UserNotFoundException('username', username)
        return UserInDb(**user)

    def get_user_by_token(self, token: str) -> User:
        session = self.get_session_by_token(token)
        return self.get_user_by_id(session.user_id)

    def create_session(self, session: SessionCreate):
        self.cursor.execute('INSERT INTO sessions (token, user_id, expires_at) values (?,?,?)',
                            (session.token, session.user_id, session.expires_at_str))
        self.conn.commit()

    def delete_session(self, session_id: int):
        self.cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
        self.conn.commit()

    def get_session_by_token(self, token: str) -> Session:
        self.cursor.execute('SELECT * FROM sessions WHERE token = ?', (token,))
        session = self.cursor.fetchone()

        if session is None:
            raise SessionNotFoundException(token)

        return Session(**session)

    def create_task(self, task: TaskCreate) -> TaskInDb:
        self.cursor.execute('INSERT INTO tasks (name, description, alert_date_time, user_id) values (?,?,?,?)',
                            (task.name, task.description, task.alert_date_str,
                             task.user_id))
        self.conn.commit()

        self.cursor.execute('SELECT * FROM tasks WHERE id = ?', (self.cursor.lastrowid,))
        task_created = self.cursor.fetchone()
        return TaskInDb(**task_created)

    def get_task_by_id(self, task_id: int) -> TaskInDb:
        self.cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = self.cursor.fetchone()
        if task is None:
            raise TaskNotFoundException(str(task_id))
        return TaskInDb(**task)

    def get_tasks_by_user_id(self, user_id: int) -> list[TaskInDb]:
        self.cursor.execute('SELECT * FROM tasks WHERE user_id = ?',
                            (user_id,))
        tasks = self.cursor.fetchall()

        return [TaskInDb(**task) for task in tasks]

    def update_task(self, task: TaskUpdate):
        self.cursor.execute('UPDATE tasks SET name = ?, description = ?, alert_date_time = ? WHERE id = ?',
                            (task.name, task.description, task.alert_date_str, task.id))
        self.conn.commit()

        self.cursor.execute('SELECT * FROM tasks WHERE id = ?', (task.id,))
        updated_task = self.cursor.fetchone()

        return TaskInDb(**updated_task)

    def delete_task(self, task_id: int):
        self.cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.conn.commit()
