import secrets
import sqlite3
from contextlib import closing
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Annotated

import bcrypt
from fastapi import Cookie, Depends, FastAPI, HTTPException, Response
from fastapi.responses import FileResponse

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "todo.db"
SESSION_COOKIE = "session_id"

app = FastAPI(title="Todo API")

class TaskCreation(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    done: bool

class User(BaseModel):
    login: Annotated[str, Field(max_length=50, min_length=1)]
    password: Annotated[str, Field(min_length=8)]



def is_invalid(title):
    if len(title) > 200 or title == "":
       return True
    else: return False

def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def execute(sql, params=()):
    with closing(connect()) as connection:
        rows = connection.execute(sql, params).fetchall()
        connection.commit()
        return rows


execute(
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        done INTEGER NOT NULL DEFAULT 0,
        user_id INTEGER NOT NULL REFERENCES users(id)
    )
    """
)
execute(
    """
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
    )
    """
)
execute(
    """
    CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id)
    )
    """
)



def as_task(row):
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


def as_user(row):
    return {"id": row["id"], "login": row["login"]}


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password, password_hash):
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def new_session_token():
    return secrets.token_hex(32)

def create_session(user_id, response):
    token = new_session_token()
    execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        samesite="lax"
    )


def current_session():
    """
    Dependency: resolve the session_id cookie to a session row joined with its user.

    Cookie: session_id
    Returns: row with at least session id, user id and login.
    Raises: HTTPException 401 {"detail": "Not logged in"}  # missing or unknown session_id
    """
    raise NotImplementedError


@app.get("/")
def index():
    return FileResponse("index.html")


@app.get("/tasks")
def list_tasks():
    rows = execute("SELECT * FROM tasks ORDER BY done ASC, id DESC")
    return [as_task(task) for task in rows]




@app.post("/tasks", status_code=201)
def create_task(task: TaskCreation):

    task.title = task.title.strip()

    if is_invalid(task.title):
        raise HTTPException(status_code=422, detail="Invalid or blank title")
    else:
        execute(
            'INSERT INTO tasks (title, done) VALUES (?, ?)',
            (task.title, 0),
        )
        rows = execute(
            'SELECT id, title, done FROM tasks WHERE title = ? ORDER BY id DESC LIMIT 1',
            (task.title,),
        )

        return as_task(rows[0])


@app.patch("/tasks/{task_id}")
def update_task(task_id: int):
    """
    Toggle a task between done and not done.

    Path params: task_id: int
    Request body: {"done": bool}
    Response 200: {"id": int, "title": str, "done": bool}
    Response 404: {"detail": "Task not found"}
    """
    raise NotImplementedError


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    """
    Delete a task.

    Path params: task_id: int
    Request body: none.
    Response 204: no body.
    Response 404: {"detail": "Task not found"}
    """
    raise NotImplementedError


@app.post("/register", status_code=201)
def register(user: User, response: Response):
    if not user.login.strip():
        raise HTTPException(status_code=422, detail="Invaild login")

    password_hashed = hash_password(user.password)
    try:
        execute("INSERT INTO users (login, password) VALUES (?, ?)", (user.login, password_hashed))
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Login already taken")

    rows = execute(
        "SELECT id, login FROM users WHERE login = ?",
        (user.login,)
    )

    create_session(rows[0]["id"], response)

    return as_user(rows[0])


@app.post("/login")
def login(user: User, response: Response):

    rows = execute("SELECT * FROM users WHERE login = ?", (user.login,))
    if not rows:
        raise HTTPException(status_code=401, detail="Invalid login or password")
    if not check_password(user.password, rows[0]["password"]):
        raise HTTPException(status_code=401, detail="Invalid login or password"        )

    create_session(rows[0]["id"], response)

    return as_user(rows[0])

    """
    Check credentials and start a session.

    Request body: {"login": str, "password": str}
    Response 200: {"id": int, "login": str}
        + Set-Cookie: session_id=<random token>; HttpOnly; SameSite=Lax
        (the token is stored in the sessions table together with the user id)
    Response 401: {"detail": "Invalid login or password"}
    """
    # raise NotImplementedError


@app.get("/me")
def me():
    """
    Return the user owning the current session.

    Cookie: session_id
    Request body: none.
    Response 200: {"id": int, "login": str}
    Response 401: {"detail": "Not logged in"}  # missing or unknown session_id
    """
    raise NotImplementedError


@app.post("/logout", status_code=204)
def logout():
    """
    End the current session.

    Cookie: session_id
    Request body: none.
    Response 204: no body; the session row is deleted and the cookie is cleared.
    Response 401: {"detail": "Not logged in"}
    """
    raise NotImplementedError
