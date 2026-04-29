import json

from pydantic import BaseModel, Field, ValidationError


class LLMOutput(BaseModel):
    summary: str = Field(..., description="One-paragraph summary of the call.")
    sentiment: str = Field(..., description="positive, neutral, negative, or mixed")
    follow_up_needed: bool = Field(..., description="Whether the customer needs follow-up.")
    key_points: list[str] = Field(..., description="Important points extracted from the call.")
    next_action: str = Field(..., description="Recommended next step for the agent.")


def parse_llm_output(raw_text: str) -> LLMOutput:
    try:
        return LLMOutput.model_validate_json(raw_text)
    except ValidationError:
        cleaned_text = raw_text.strip()
        return LLMOutput.model_validate(json.loads(cleaned_text))
