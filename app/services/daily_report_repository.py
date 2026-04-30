from datetime import date

from app.core.database import get_db_connection
from app.schemas.report import DailyReportResult


class DailyReportRepository:
    def save_report(self, report: DailyReportResult) -> int:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    insert into daily_reports (
                        report_date,
                        report_timezone,
                        total_calls,
                        positive_count,
                        neutral_count,
                        negative_count,
                        mixed_count,
                        follow_up_count,
                        subject,
                        recipients,
                        html_content,
                        send_status,
                        error_message,
                        updated_at
                    )
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())
                    on conflict (report_date, report_timezone)
                    do update set
                        total_calls = excluded.total_calls,
                        positive_count = excluded.positive_count,
                        neutral_count = excluded.neutral_count,
                        negative_count = excluded.negative_count,
                        mixed_count = excluded.mixed_count,
                        follow_up_count = excluded.follow_up_count,
                        subject = excluded.subject,
                        recipients = excluded.recipients,
                        html_content = excluded.html_content,
                        send_status = excluded.send_status,
                        error_message = excluded.error_message,
                        updated_at = now()
                    returning id
                    """,
                    (
                        report.report_date,
                        report.report_timezone,
                        report.total_calls,
                        report.positive_count,
                        report.neutral_count,
                        report.negative_count,
                        report.mixed_count,
                        report.follow_up_count,
                        report.subject,
                        report.recipients,
                        report.html_content,
                        report.send_status,
                        report.error_message,
                    ),
                )
                row = cursor.fetchone()

        if not row:
            raise RuntimeError(f"Failed to save daily report for {report.report_date}")

        return int(row["id"])

    def get_report(self, report_date: date, report_timezone: str) -> dict | None:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    select *
                    from daily_reports
                    where report_date = %s and report_timezone = %s
                    """,
                    (report_date, report_timezone),
                )
                return cursor.fetchone()
