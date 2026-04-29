from dotenv import load_dotenv
load_dotenv()
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.services.call_processor import process_call_record
from app.services.call_source import load_call_from_txt, load_calls_from_txt


def _resolve_input_file() -> Path:
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
        if not file_path.is_absolute():
            file_path = PROJECT_ROOT / file_path
        return file_path

    all_calls = sorted(settings.raw_calls_path.glob("*.txt"))
    if not all_calls:
        raise FileNotFoundError(f"No txt files found under {settings.raw_calls_path}")
    return all_calls[0]


def run_single_demo() -> None:
    input_file = _resolve_input_file()
    call_record = load_call_from_txt(input_file)
    result = process_call_record(call_record)
    raw_call_id = result["raw_call_id"]
    analysis_id = result["analysis_id"]
    final_state = result["final_state"]

    print("=" * 80)
    print(f"Call ID: {call_record.call_id}")
    print(f"Source File: {call_record.file_name}")
    print(f"Phone: {call_record.customer_phone}")
    print(f"Email: {call_record.customer_email}")
    print("-" * 80)
    print("Original Transcript:")
    print(call_record.transcript_raw)
    print("-" * 80)
    print("Masked Transcript:")
    print(final_state["masked_transcript"])
    print("-" * 80)
    print("Raw LLM Output:")
    print(final_state["llm_raw_output"])
    print("-" * 80)
    print("Parsed JSON Result:")
    print(json.dumps(final_state["parsed_output"], ensure_ascii=False, indent=2))
    print("-" * 80)
    print(f"Saved raw_calls.id: {raw_call_id}")
    print(f"Saved call_analysis.id: {analysis_id}")
    print(f"Database URL: {settings.database_url}")
    print("=" * 80)


def list_inputs() -> None:
    calls = load_calls_from_txt(settings.raw_calls_path)
    print("Available txt inputs:")
    for call in calls:
        print(f"- {call.call_id}: {call.file_name}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_inputs()
    else:
        run_single_demo()
