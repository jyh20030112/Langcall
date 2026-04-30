from fastapi import APIRouter

from app.schemas.mail import MailTestRequest, MailTestResponse
from app.services.email_service import EmailService


router = APIRouter(prefix="/mail", tags=["mail"])


@router.post("/test", response_model=MailTestResponse)
def send_mailpit_test_email(payload: MailTestRequest) -> MailTestResponse:
    result = EmailService().send_test_email(
        to_email=payload.to_email,
        subject=payload.subject,
        message=payload.message,
    )
    return MailTestResponse(**result)
