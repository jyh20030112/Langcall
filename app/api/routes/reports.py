from datetime import date

from fastapi import APIRouter

from app.schemas.report import DailyReportRequest, DailyReportResponse
from app.services.report_service import ReportService


router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/daily/send", response_model=DailyReportResponse)
def send_daily_report(payload: DailyReportRequest) -> DailyReportResponse:
    report = ReportService().send_daily_report(
        report_date=payload.report_date,
        recipient=payload.recipient,
    )
    return DailyReportResponse(
        status=report.send_status,
        report_date=report.report_date,
        report_timezone=report.report_timezone,
        total_calls=report.total_calls,
        recipients=report.recipients,
        subject=report.subject,
    )


@router.get("/daily/{report_date}")
def get_daily_report(report_date: date) -> dict:
    report = ReportService().get_saved_report(report_date)
    if report is None:
        return {"status": "not_found", "report_date": report_date.isoformat()}
    return report
