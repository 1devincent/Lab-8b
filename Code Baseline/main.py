"""Task Management API built with FastAPI and SQLite.

Exposes ``create_app(database_path)`` so tests can point each app at a
fresh SQLite file, and provides a module-level ``app`` for Uvicorn.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import asynccontextmanager
from typing import Annotated, Iterator, Union

from fastapi import Depends, FastAPI, HTTPException, Path
from pydantic import BaseModel, ConfigDict, Field, field_validator

DEFAULT_DB_PATH = os.getenv("TASKS_DB_PATH", "tasks.db")

DatabasePath = Union[str, "os.PathLike[str]"]


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------
class TaskCreate(BaseModel):
    """Payload for POST /tasks."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=120)
    completed: bool = Field(default=False, strict=True)

    @field_validator("title", mode="before")
    @classmethod
    def _strip_title(cls, value: object) -> object:
        # Trim before length validation so that whitespace-only titles fail
        # the min_length check.
        if isinstance(value, str):
            return value.strip()
        return value


class TaskUpdate(BaseModel):
    """Payload for PATCH /tasks/{id}."""

    model_config = ConfigDict(extra="forbid")

    completed: bool = Field(..., strict=True)


class TaskOut(BaseModel):
    """Response body for task endpoints."""

    id: int
    title: str
    completed: bool


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def init_db(database_path: DatabasePath) -> None:
    """Create the tasks table if it does not exist yet."""
    conn = sqlite3.connect(str(database_path))
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def _row_to_task(row: sqlite3.Row) -> TaskOut:
    return TaskOut(id=row["id"], title=row["title"], completed=bool(row["completed"]))


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
def create_app(database_path: DatabasePath) -> FastAPI:
    """Build a FastAPI app bound to the given SQLite database file."""
    db_path = str(database_path)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> Iterator[None]:
        init_db(db_path)
        yield

    app = FastAPI(title="Task Management API", version="1.0.0", lifespan=lifespan)

    def get_db() -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # ----------------------------- POST /tasks -----------------------------
    @app.post("/tasks", status_code=201, response_model=TaskOut)
    def create_task(
        task: TaskCreate,
        db: Annotated[sqlite3.Connection, Depends(get_db)],
    ) -> TaskOut:
        cursor = db.execute(
            "INSERT INTO tasks (title, completed) VALUES (?, ?)",
            (task.title, 1 if task.completed else 0),
        )
        db.commit()
        row = db.execute(
            "SELECT id, title, completed FROM tasks WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
        assert row is not None  # just inserted
        return _row_to_task(row)

    # -------------------------- GET /tasks/{id} ----------------------------
    @app.get("/tasks/{task_id}", response_model=TaskOut)
    def get_task(
        task_id: Annotated[int, Path(ge=1)],
        db: Annotated[sqlite3.Connection, Depends(get_db)],
    ) -> TaskOut:
        row = db.execute(
            "SELECT id, title, completed FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return _row_to_task(row)

    # ------------------------- PATCH /tasks/{id} ---------------------------
    @app.patch("/tasks/{task_id}", response_model=TaskOut)
    def update_task(
        task_id: Annotated[int, Path(ge=1)],
        task: TaskUpdate,
        db: Annotated[sqlite3.Connection, Depends(get_db)],
    ) -> TaskOut:
        row = db.execute(
            "SELECT id, title, completed FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")

        db.execute(
            "UPDATE tasks SET completed = ? WHERE id = ?",
            (1 if task.completed else 0, task_id),
        )
        db.commit()

        row = db.execute(
            "SELECT id, title, completed FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        assert row is not None
        return _row_to_task(row)

    return app


# Module-level app for `uvicorn app.main:app`
app = create_app(DEFAULT_DB_PATH)   