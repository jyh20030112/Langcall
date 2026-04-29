from pydantic import BaseModel, Field


class CallRecord(BaseModel):
    call_id: str = Field(..., description="Unique call id derived from the file name.")
    source: str = Field(default="txt_demo", description="Input source for the call.")
    file_name: str = Field(..., description="Original text file name.")
    transcript_raw: str = Field(..., description="Full conversation text loaded from file.")
    customer_phone: str | None = Field(default=None, description="Phone number found in header.")
    customer_email: str | None = Field(default=None, description="Email found in header.")
