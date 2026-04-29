from typing import Any

from app.core.config import settings
from app.graph.workflow import build_workflow
from app.schemas.call_record import CallRecord
from app.services.analysis_repository import AnalysisRepository
from app.services.dead_letter_repository import DeadLetterRepository
from app.services.raw_call_repository import RawCallRepository
from app.services.redis_guard import build_call_processing_lock, release_webhook_guard, try_acquire_webhook_guard
from app.services.task_repository import TaskRepository


def _analyze_raw_call(raw_call_id: int, call_record: CallRecord) -> dict[str, Any]:
    workflow = build_workflow()
    final_state = workflow.invoke(call_record.model_dump())

    analysis_repository = AnalysisRepository()
    analysis_id = analysis_repository.save_analysis(
        raw_call_id=raw_call_id,
        call_id=call_record.call_id,
        llm_raw_output=final_state["llm_raw_output"],
        result=final_state["parsed_output"],
    )

    return {
        "raw_call_id": raw_call_id,
        "analysis_id": analysis_id,
        "final_state": final_state,
    }


def process_call_record(call_record: CallRecord) -> dict[str, Any]:
    raw_call_repository = RawCallRepository()
    raw_call_id = raw_call_repository.save_raw_call(call_record)
    return _analyze_raw_call(raw_call_id=raw_call_id, call_record=call_record)


def enqueue_call_record(call_record: CallRecord) -> dict[str, Any]:
    guard = try_acquire_webhook_guard(call_record.call_id)
    task_repository = TaskRepository()

    if not guard.acquired:
        existing_task = task_repository.get_task_by_call_id(call_record.call_id)
        if existing_task:
            return {
                "task_id": existing_task.id,
                "raw_call_id": existing_task.raw_call_id,
                "call_id": existing_task.call_id,
                "task_status": existing_task.task_status,
                "is_duplicate": True,
            }

        return {
            "task_id": 0,
            "raw_call_id": 0,
            "call_id": call_record.call_id,
            "task_status": "duplicate_inflight",
            "is_duplicate": True,
        }

    raw_call_repository = RawCallRepository()
    try:
        raw_call_id = raw_call_repository.save_raw_call(call_record)
        task = task_repository.enqueue_task(raw_call_id=raw_call_id, call_id=call_record.call_id)
        return task.model_dump()
    finally:
        release_webhook_guard(call_record.call_id, guard.token)


def process_pending_task(worker_id: str) -> dict[str, Any] | None:
    task_repository = TaskRepository()
    task = task_repository.claim_next_pending_task(worker_id)

    if task is None:
        return None

    raw_call_repository = RawCallRepository()
    processing_lock = build_call_processing_lock(task.call_id)

    try:
        if not processing_lock.acquire():
            task_repository.mark_retrying(
                task_id=task.id,
                error_message=f"redis lock not acquired for call_id={task.call_id}",
                retry_count=task.retry_count,
                delay_seconds=1,
            )
            return {
                "task_id": task.id,
                "call_id": task.call_id,
                "raw_call_id": task.raw_call_id,
                "analysis_id": None,
            }

        call_record = raw_call_repository.get_raw_call_by_id(task.raw_call_id)
        result = _analyze_raw_call(raw_call_id=task.raw_call_id, call_record=call_record)
        task_repository.mark_success(task.id)
        return {
            "task_id": task.id,
            "call_id": task.call_id,
            "raw_call_id": result["raw_call_id"],
            "analysis_id": result["analysis_id"],
        }
    except Exception as exc:
        next_retry_count = task.retry_count + 1
        error_message = str(exc)
        if next_retry_count <= settings.max_retry_count:
            delay_seconds = settings.retry_backoff_base_seconds ** next_retry_count
            task_repository.mark_retrying(
                task_id=task.id,
                error_message=error_message,
                retry_count=next_retry_count,
                delay_seconds=delay_seconds,
            )
            return {
                "task_id": task.id,
                "call_id": task.call_id,
                "raw_call_id": task.raw_call_id,
                "analysis_id": None,
                "retry_scheduled_in_seconds": delay_seconds,
            }

        call_record = raw_call_repository.get_raw_call_by_id(task.raw_call_id)
        dead_letter_id = DeadLetterRepository().add_dead_letter(
            task_id=task.id,
            raw_call_id=task.raw_call_id,
            call_id=task.call_id,
            failed_stage="langgraph_analysis",
            error_message=error_message,
            payload={
                "call_record": call_record.model_dump(),
                "retry_count": next_retry_count,
                "worker_id": worker_id,
            },
        )
        task_repository.mark_dead(
            task_id=task.id,
            error_message=error_message,
            retry_count=next_retry_count,
        )
        return {
            "task_id": task.id,
            "call_id": task.call_id,
            "raw_call_id": task.raw_call_id,
            "analysis_id": None,
            "dead_letter_id": dead_letter_id,
        }
    finally:
        try:
            if processing_lock.owned():
                processing_lock.release()
        except Exception:
            pass
