from typing import Any, TypedDict


class CallGraphState(TypedDict, total=False):
    call_id: str
    file_name: str
    customer_phone: str | None
    customer_email: str | None
    transcript_raw: str
    transcript_clean: str
    masked_transcript: str
    prompt: str
    llm_raw_output: str
    parsed_output: dict[str, Any]
