from pathlib import Path

from app.schemas.call_record import CallRecord


def _extract_metadata(lines: list[str]) -> tuple[str | None, str | None, list[str]]:
    phone = None
    email = None
    conversation_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("手机号："):
            phone = stripped.split("：", 1)[1].strip() or None
            continue
        if stripped.startswith("邮箱："):
            email = stripped.split("：", 1)[1].strip() or None
            continue
        conversation_lines.append(stripped)

    return phone, email, conversation_lines


def load_call_from_txt(file_path: Path) -> CallRecord:
    raw_text = file_path.read_text(encoding="utf-8").strip()
    lines = raw_text.splitlines()
    phone, email, conversation_lines = _extract_metadata(lines)
    transcript_raw = "\n".join(conversation_lines).strip()

    if not transcript_raw:
        raise ValueError(f"{file_path.name} does not contain conversation content.")

    return CallRecord(
        call_id=file_path.stem,
        source="txt_demo",
        file_name=file_path.name,
        transcript_raw=transcript_raw,
        customer_phone=phone,
        customer_email=email,
    )


def load_calls_from_txt(directory: Path) -> list[CallRecord]:
    files = sorted(directory.glob("*.txt"))
    return [load_call_from_txt(file_path) for file_path in files]
