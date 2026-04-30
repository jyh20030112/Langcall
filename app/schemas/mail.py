from pydantic import BaseModel, Field


class MailTestRequest(BaseModel):
    to_email: str | None = Field(default=None, description="Optional recipient email.")
    subject: str = Field(default="LangCall Mailpit Test", description="Email subject.")
    message: str = Field(
        default="This is a Mailpit test email from LangCall.",
        description="Plain text message body.",
    )


class MailTestResponse(BaseModel):
    status: str
    smtp_host: str
    smtp_port: int
    to_email: str
    subject: str
