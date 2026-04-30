from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.core.config import settings
from app.core.database import get_db_connection
from app.schemas.report import DailyReportCallItem, DailyReportResult
from app.services.daily_report_repository import DailyReportRepository
from app.services.email_service import EmailService


class ReportService:
    def build_daily_report(
        self,
        report_date: date | None = None,
        recipient: str | None = None,
    ) -> DailyReportResult:
        timezone_name = settings.report_timezone
        target_date = report_date or datetime.now(ZoneInfo(timezone_name)).date()
        recipients = recipient or settings.report_to

        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    select
                        ca.call_id,
                        ca.sentiment,
                        ca.follow_up_needed,
                        ca.summary,
                        ca.next_action,
                        ca.created_at
                    from call_analysis ca
                    where timezone(%s, ca.created_at)::date = %s
                    order by ca.created_at asc
                    """,
                    (timezone_name, target_date),
                )
                rows = cursor.fetchall()

        call_items = [DailyReportCallItem.model_validate(row) for row in rows]

        positive_count = sum(1 for item in call_items if item.sentiment == "positive")
        neutral_count = sum(1 for item in call_items if item.sentiment == "neutral")
        negative_count = sum(1 for item in call_items if item.sentiment == "negative")
        mixed_count = sum(1 for item in call_items if item.sentiment == "mixed")
        follow_up_count = sum(1 for item in call_items if item.follow_up_needed)

        subject = f"LangCall Daily Report - {target_date.isoformat()} ({timezone_name})"
        html_content = self._build_html(
            report_date=target_date,
            timezone_name=timezone_name,
            call_items=call_items,
            positive_count=positive_count,
            neutral_count=neutral_count,
            negative_count=negative_count,
            mixed_count=mixed_count,
            follow_up_count=follow_up_count,
        )

        return DailyReportResult(
            report_date=target_date,
            report_timezone=timezone_name,
            total_calls=len(call_items),
            positive_count=positive_count,
            neutral_count=neutral_count,
            negative_count=negative_count,
            mixed_count=mixed_count,
            follow_up_count=follow_up_count,
            subject=subject,
            recipients=recipients,
            html_content=html_content,
            calls=call_items,
        )

    def send_daily_report(
        self,
        report_date: date | None = None,
        recipient: str | None = None,
    ) -> DailyReportResult:
        report = self.build_daily_report(report_date=report_date, recipient=recipient)
        try:
            EmailService().send_html_email(
                to_email=report.recipients,
                subject=report.subject,
                html_content=report.html_content,
            )
            report.send_status = "success"
            report.error_message = None
        except Exception as exc:
            report.send_status = "failed"
            report.error_message = str(exc)
            DailyReportRepository().save_report(report)
            raise

        DailyReportRepository().save_report(report)
        return report

    def get_saved_report(self, report_date: date) -> dict | None:
        return DailyReportRepository().get_report(report_date, settings.report_timezone)

    def _build_html(
        self,
        report_date: date,
        timezone_name: str,
        call_items: list[DailyReportCallItem],
        positive_count: int,
        neutral_count: int,
        negative_count: int,
        mixed_count: int,
        follow_up_count: int,
    ) -> str:
        list_items = []
        for item in call_items:
            list_items.append(
                "<li>"
                f"<strong>{item.call_id}</strong> | 情绪: {item.sentiment} | "
                f"需跟进: {'是' if item.follow_up_needed else '否'}<br>"
                f"摘要: {item.summary}<br>"
                f"建议动作: {item.next_action}"
                "</li>"
            )

        details = "".join(list_items) if list_items else "<li>当天没有分析记录。</li>"

        return f"""
        <html>
          <body>
            <h2>LangCall 日报</h2>
            <p>日期：{report_date.isoformat()}（{timezone_name}）</p>
            <ul>
              <li>总通话数：{len(call_items)}</li>
              <li>正向：{positive_count}</li>
              <li>中性：{neutral_count}</li>
              <li>负向：{negative_count}</li>
              <li>混合：{mixed_count}</li>
              <li>需跟进：{follow_up_count}</li>
            </ul>
            <hr>
            <ol>
              {details}
            </ol>
          </body>
        </html>
        """.strip()
