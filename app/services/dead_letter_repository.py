import json
from typing import Any

from app.core.database import get_db_connection


class DeadLetterRepository:
    def add_dead_letter(
        self,
        task_id: int,
        raw_call_id: int,
        call_id: str,
        failed_stage: str,
        error_message: str,
        payload: dict[str, Any],
    ) -> int:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    insert into dead_letter_queue (
                        task_id,
                        raw_call_id,
                        call_id,
                        failed_stage,
                        error_message,
                        payload
                    )
                    values (%s, %s, %s, %s, %s, %s::jsonb)
                    returning id
                    """,
                    (
                        task_id,
                        raw_call_id,
                        call_id,
                        failed_stage,
                        error_message,
                        json.dumps(payload, ensure_ascii=False),
                    ),
                )
                row = cursor.fetchone()

        if not row:
            raise RuntimeError(f"Failed to store dead letter for task_id={task_id}")

        return int(row["id"])
