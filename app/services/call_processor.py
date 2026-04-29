from typing import Any

from app.graph.workflow import build_workflow
from app.schemas.call_record import CallRecord
from app.services.analysis_repository import AnalysisRepository
from app.services.raw_call_repository import RawCallRepository
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
    raw_call_repository = RawCallRepository()
    raw_call_id = raw_call_repository.save_raw_call(call_record)

    task_repository = TaskRepository()
    task = task_repository.enqueue_task(raw_call_id=raw_call_id, call_id=call_record.call_id)
    return task.model_dump()


def process_pending_task(worker_id: str) -> dict[str, Any] | None:
    task_repository = TaskRepository()
    task = task_repository.claim_next_pending_task(worker_id)

    if task is None:
        return None

    raw_call_repository = RawCallRepository()

    try:
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
        task_repository.mark_failed(task.id, str(exc))
        raise
