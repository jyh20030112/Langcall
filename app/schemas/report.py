from datetime import date, datetime

from pydantic import BaseModel, Field


class DailyReportCallItem(BaseModel):
    call_id: str
    sentiment: str
    follow_up_needed: bool
    summary: str
    next_action: str
    created_at: datetime


class DailyReportResult(BaseModel):
    report_date: date
    report_timezone: str
    total_calls: int
    positive_count: int
    neutral_count: int
    negative_count: int
    mixed_count: int
    follow_up_count: int
    subject: str
    recipients: str
    html_content: str
    send_status: str = "success"
    error_message: str | None = None
    calls: list[DailyReportCallItem] = Field(default_factory=list)


class DailyReportRequest(BaseModel):
    report_date: date | None = None
    recipient: str | None = None


class DailyReportResponse(BaseModel):
    status: str
    report_date: date
    report_timezone: str
    total_calls: int
    recipients: str
    subject: str
