import smtplib
from email.message import EmailMessage

from app.core.config import settings


class EmailService:
    def send_plain_email(
        self,
        to_email: str | None = None,
        subject: str = "LangCall Mailpit Test",
        message: str = "This is a Mailpit test email from LangCall.",
    ) -> dict[str, str | int]:
        recipient = to_email or settings.report_to

        email_message = EmailMessage()
        email_message["From"] = settings.smtp_from
        email_message["To"] = recipient
        email_message["Subject"] = subject
        email_message.set_content(message)

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            smtp.send_message(email_message)

        return {
            "status": "sent",
            "smtp_host": settings.smtp_host,
            "smtp_port": settings.smtp_port,
            "to_email": recipient,
            "subject": subject,
        }

    def send_html_email(
        self,
        to_email: str | None = None,
        subject: str = "LangCall HTML Mail",
        html_content: str = "<p>This is a Mailpit HTML email from LangCall.</p>",
    ) -> dict[str, str | int]:
        recipient = to_email or settings.report_to

        email_message = EmailMessage()
        email_message["From"] = settings.smtp_from
        email_message["To"] = recipient
        email_message["Subject"] = subject
        email_message.set_content("Please view this email in an HTML-compatible client.")
        email_message.add_alternative(html_content, subtype="html")

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            smtp.send_message(email_message)

        return {
            "status": "sent",
            "smtp_host": settings.smtp_host,
            "smtp_port": settings.smtp_port,
            "to_email": recipient,
            "subject": subject,
        }

    def send_test_email(
        self,
        to_email: str | None = None,
        subject: str = "LangCall Mailpit Test",
        message: str = "This is a Mailpit test email from LangCall.",
    ) -> dict[str, str | int]:
        return self.send_plain_email(
            to_email=to_email,
            subject=subject,
            message=message,
        )
