import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

load_dotenv()

from app.services.email_service import EmailService


def main() -> None:
    result = EmailService().send_test_email()
    print("Mailpit test email sent.")
    print(f"SMTP Host: {result['smtp_host']}")
    print(f"SMTP Port: {result['smtp_port']}")
    print(f"Recipient: {result['to_email']}")
    print(f"Subject: {result['subject']}")


if __name__ == "__main__":
    main()
