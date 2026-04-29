from app.core.database import get_db_connection
from app.schemas.call_record import CallRecord


class RawCallRepository:
    """Stores raw call inputs in PostgreSQL."""

    def save_raw_call(self, call_record: CallRecord) -> int:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    insert into raw_calls (
                        call_id,
                        source,
                        file_name,
                        customer_phone,
                        customer_email,
                        transcript_raw
                    )
                    values (%s, %s, %s, %s, %s, %s)
                    on conflict (call_id)
                    do update set
                        source = excluded.source,
                        file_name = excluded.file_name,
                        customer_phone = excluded.customer_phone,
                        customer_email = excluded.customer_email,
                        transcript_raw = excluded.transcript_raw
                    returning id
                    """,
                    (
                        call_record.call_id,
                        call_record.source,
                        call_record.file_name,
                        call_record.customer_phone,
                        call_record.customer_email,
                        call_record.transcript_raw,
                    ),
                )
                row = cursor.fetchone()

        if not row:
            raise RuntimeError(f"Failed to save raw call: {call_record.call_id}")

        return int(row["id"])

    def get_raw_call_by_id(self, raw_call_id: int) -> CallRecord:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    select call_id, source, file_name, transcript_raw, customer_phone, customer_email
                    from raw_calls
                    where id = %s
                    """,
                    (raw_call_id,),
                )
                row = cursor.fetchone()

        if not row:
            raise RuntimeError(f"raw_calls record not found: {raw_call_id}")

        return CallRecord(
            call_id=row["call_id"],
            source=row["source"],
            file_name=row["file_name"],
            transcript_raw=row["transcript_raw"],
            customer_phone=row["customer_phone"],
            customer_email=row["customer_email"],
        )
