from datetime import datetime

from pydantic import BaseModel, Field


class CallTask(BaseModel):
    id: int
    raw_call_id: int
    call_id: str
    task_status: str
    retry_count: int = 0
    locked_by: str | None = None
    last_error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class EnqueueTaskResult(BaseModel):
    task_id: int = Field(..., description="Task id in call_tasks.")
    raw_call_id: int = Field(..., description="Related raw_calls id.")
    call_id: str
    task_status: str
    is_duplicate: bool = False
