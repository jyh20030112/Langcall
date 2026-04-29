from fastapi import APIRouter

from app.schemas.call_record import CallRecord
from app.schemas.webhook import CallWebhookRequest, CallWebhookResponse
from app.services.call_processor import process_call_record


router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/calls", response_model=CallWebhookResponse)
def ingest_call_webhook(payload: CallWebhookRequest) -> CallWebhookResponse:
    call_record = CallRecord(
        call_id=payload.call_id,
        source=payload.source,
        file_name=payload.file_name or f"{payload.call_id}.json",
        transcript_raw=payload.transcript_raw,
        customer_phone=payload.customer_phone,
        customer_email=payload.customer_email,
    )
    result = process_call_record(call_record)
    return CallWebhookResponse(
        status="success",
        raw_call_id=result["raw_call_id"],
        analysis_id=result["analysis_id"],
        call_id=call_record.call_id,
    )
