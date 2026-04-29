import json

from app.core.database import get_db_connection


class AnalysisRepository:
    """Stores structured analysis results in PostgreSQL."""

    def save_analysis(
        self,
        raw_call_id: int,
        call_id: str,
        llm_raw_output: str,
        result: dict,
    ) -> int:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "delete from call_analysis where raw_call_id = %s",
                    (raw_call_id,),
                )
                cursor.execute(
                    """
                    insert into call_analysis (
                        raw_call_id,
                        call_id,
                        llm_raw_output,
                        summary,
                        sentiment,
                        follow_up_needed,
                        key_points,
                        next_action,
                        parsed_output
                    )
                    values (%s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s::jsonb)
                    returning id
                    """,
                    (
                        raw_call_id,
                        call_id,
                        llm_raw_output,
                        result["summary"],
                        result["sentiment"],
                        result["follow_up_needed"],
                        json.dumps(result["key_points"], ensure_ascii=False),
                        result["next_action"],
                        json.dumps(result, ensure_ascii=False),
                    ),
                )
                row = cursor.fetchone()

        if not row:
            raise RuntimeError(f"Failed to save analysis for call: {call_id}")

        return int(row["id"])
