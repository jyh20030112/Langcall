from typing import Any

from app.graph.workflow import build_workflow
from app.schemas.call_record import CallRecord
from app.services.analysis_repository import AnalysisRepository
from app.services.raw_call_repository import RawCallRepository


def process_call_record(call_record: CallRecord) -> dict[str, Any]:
    raw_call_repository = RawCallRepository()
    raw_call_id = raw_call_repository.save_raw_call(call_record)

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
