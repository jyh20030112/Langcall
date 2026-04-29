from pydantic import BaseModel, Field


class CallWebhookRequest(BaseModel):
    call_id: str = Field(..., description="Unique call id from the upstream system.")
    transcript_raw: str = Field(..., description="Full raw conversation text.")
    source: str = Field(default="api_webhook", description="Incoming event source.")
    file_name: str | None = Field(default=None, description="Optional logical file name.")
    customer_phone: str | None = Field(default=None, description="Optional customer phone.")
    customer_email: str | None = Field(default=None, description="Optional customer email.")


class CallWebhookResponse(BaseModel):
    status: str
    raw_call_id: int
    analysis_id: int
    call_id: str
