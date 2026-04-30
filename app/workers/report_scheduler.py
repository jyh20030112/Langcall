import time
from datetime import date, datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from app.core.config import settings
from app.services.daily_report_repository import DailyReportRepository
from app.services.report_service import ReportService


load_dotenv()


def run_scheduler_loop() -> None:
    timezone = ZoneInfo(settings.report_timezone)
    print(
        f"[report_scheduler] started timezone={settings.report_timezone} "
        f"hour={settings.report_hour} minute={settings.report_minute}"
    )
    while True:
        now = datetime.now(timezone)
        if now.hour == settings.report_hour and now.minute == settings.report_minute:
            today = now.date()
            existing = DailyReportRepository().get_report(today, settings.report_timezone)
            if not existing or existing["send_status"] != "success":
                try:
                    report = ReportService().send_daily_report(report_date=today)
                    print(
                        f"[report_scheduler] sent report date={report.report_date} "
                        f"total_calls={report.total_calls}"
                    )
                except Exception as exc:
                    print(f"[report_scheduler] failed to send report: {exc}")
            time.sleep(60)
        else:
            time.sleep(15)


if __name__ == "__main__":
    run_scheduler_loop()
