from fastapi import APIRouter

from app.schemas.call_record import CallRecord
from app.schemas.webhook import CallWebhookRequest, CallWebhookResponse
from app.services.call_processor import enqueue_call_record
from app.services.task_repository import TaskRepository


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
    result = enqueue_call_record(call_record)
    return CallWebhookResponse(
        status="queued",
        raw_call_id=result["raw_call_id"],
        task_id=result["task_id"],
        call_id=call_record.call_id,
    )


@router.get("/tasks/{task_id}")
def get_task_status(task_id: int) -> dict:
    task = TaskRepository().get_task_by_id(task_id)
    if task is None:
        return {"status": "not_found", "task_id": task_id}
    return task.model_dump(mode="json")
