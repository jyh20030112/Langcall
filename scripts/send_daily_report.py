from datetime import date
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

load_dotenv()

from app.services.report_service import ReportService


def main() -> None:
    report_date = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else None
    report = ReportService().send_daily_report(report_date=report_date)
    print("Daily report sent.")
    print(f"Date: {report.report_date}")
    print(f"Timezone: {report.report_timezone}")
    print(f"Total Calls: {report.total_calls}")
    print(f"Recipients: {report.recipients}")
    print(f"Subject: {report.subject}")


if __name__ == "__main__":
    main()
