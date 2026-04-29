from app.core.database import get_db_connection
from app.schemas.task import CallTask, EnqueueTaskResult


class TaskRepository:
    def enqueue_task(self, raw_call_id: int, call_id: str) -> EnqueueTaskResult:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    select id as task_id, raw_call_id, call_id, task_status
                    from call_tasks
                    where raw_call_id = %s
                    """,
                    (raw_call_id,),
                )
                existing_row = cursor.fetchone()

                if existing_row:
                    existing_row["is_duplicate"] = True
                    return EnqueueTaskResult.model_validate(existing_row)

                cursor.execute(
                    """
                    insert into call_tasks (
                        raw_call_id,
                        call_id,
                        task_status,
                        retry_count,
                        locked_by,
                        last_error,
                        started_at,
                        completed_at,
                        updated_at
                    )
                    values (%s, %s, 'pending', 0, null, null, null, null, now())
                    returning id as task_id, raw_call_id, call_id, task_status
                    """,
                    (raw_call_id, call_id),
                )
                row = cursor.fetchone()

        if not row:
            raise RuntimeError(f"Failed to enqueue task for raw_call_id={raw_call_id}")

        row["is_duplicate"] = False
        return EnqueueTaskResult.model_validate(row)

    def claim_next_pending_task(self, worker_id: str) -> CallTask | None:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    with next_task as (
                        select id
                        from call_tasks
                        where task_status = 'pending'
                        order by created_at asc
                        for update skip locked
                        limit 1
                    )
                    update call_tasks
                    set
                        task_status = 'processing',
                        locked_by = %s,
                        started_at = now(),
                        updated_at = now()
                    where id in (select id from next_task)
                    returning *
                    """,
                    (worker_id,),
                )
                row = cursor.fetchone()

        if not row:
            return None

        return CallTask.model_validate(row)

    def mark_success(self, task_id: int) -> None:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    update call_tasks
                    set
                        task_status = 'success',
                        completed_at = now(),
                        updated_at = now(),
                        last_error = null,
                        locked_by = null
                    where id = %s
                    """,
                    (task_id,),
                )

    def mark_failed(self, task_id: int, error_message: str) -> None:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    update call_tasks
                    set
                        task_status = 'failed',
                        last_error = %s,
                        retry_count = retry_count + 1,
                        updated_at = now(),
                        locked_by = null
                    where id = %s
                    """,
                    (error_message, task_id),
                )

    def get_task_by_id(self, task_id: int) -> CallTask | None:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "select * from call_tasks where id = %s",
                    (task_id,),
                )
                row = cursor.fetchone()

        if not row:
            return None

        return CallTask.model_validate(row)

    def get_task_by_call_id(self, call_id: str) -> CallTask | None:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "select * from call_tasks where call_id = %s",
                    (call_id,),
                )
                row = cursor.fetchone()

        if not row:
            return None

        return CallTask.model_validate(row)
