import sqlite3
from contextlib import closing
from pathlib import Path
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "todo.db"

app = FastAPI(title="Todo API")


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
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
        done INTEGER NOT NULL DEFAULT 0
    )
    """
)


def as_task(row):
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

def is_invalid(title):
    if len(title) > 200 or title == "":
       return True
    else: return False

class TaskCreation(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    done: bool

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
def update_task(task_id: int, done: TaskUpdate):
    rows = execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (str(task_id),),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Task not found")
    execute(
        "UPDATE tasks SET done = ? WHERE id = ?",
        (str(int(done.done)), str(task_id))
    )
    rows = execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (str(task_id),)
    )
    return as_task(rows[0])

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    rows = execute(
        "SELECT id FROM tasks WHERE id = ?",
        (str(task_id),)
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Task not found")

    execute(
        "DELETE FROM tasks WHERE id = ?",
        (str(task_id),)
    )   

#
# todo:
# - change sql to prevent sqlinjections
# a