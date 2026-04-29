from app.graph.state import CallGraphState
from app.schemas.llm_output import parse_llm_output
from app.services.litellm_client import call_llm
from app.services.pii_masker import mask_text


def normalize_input(state: CallGraphState) -> CallGraphState:
    transcript_raw = state["transcript_raw"]
    normalized = "\n".join(line.strip() for line in transcript_raw.splitlines() if line.strip())
    return {"transcript_clean": normalized}


def mask_pii(state: CallGraphState) -> CallGraphState:
    masked_transcript = mask_text(state["transcript_clean"])
    return {"masked_transcript": masked_transcript}


def build_prompt(state: CallGraphState) -> CallGraphState:
    prompt = f"""
你是一个客服通话分析助手。
请阅读下面的中文客服通话内容，并输出一个 JSON 对象。

要求：
1. 只能输出 JSON，不要输出解释文字。
2. JSON 必须包含以下字段：
   - summary: 字符串
   - sentiment: 字符串，只能是 positive / neutral / negative / mixed 之一
   - follow_up_needed: 布尔值
   - key_points: 字符串数组
   - next_action: 字符串
3. 不要编造不存在的信息。
4. 如果客户明确拒绝沟通，follow_up_needed 应为 false。

通话内容：
{state["masked_transcript"]}
""".strip()
    return {"prompt": prompt}


def run_llm(state: CallGraphState) -> CallGraphState:
    llm_raw_output = call_llm(state["prompt"])
    return {"llm_raw_output": llm_raw_output}


def validate_output(state: CallGraphState) -> CallGraphState:
    parsed = parse_llm_output(state["llm_raw_output"])
    return {"parsed_output": parsed.model_dump()}
