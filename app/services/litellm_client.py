import json
from typing import Any

from app.core.config import settings


def _build_mock_response(prompt: str) -> str:
    lowered_prompt = prompt.lower()
    follow_up_needed = "发你微信" in prompt or "带看" in prompt or "回访" in prompt or "看看房" in prompt

    if "不需要" in prompt or "别再给我打电话" in prompt:
        sentiment = "negative"
        next_action = "标记为拒绝沟通，暂停继续外呼。"
    elif "行，那你发吧" in prompt or "抽空我去实地看看房吧" in prompt:
        sentiment = "positive"
        next_action = "记录客户意向，尽快发送房源信息并安排跟进。"
    elif "先看看吧" in prompt:
        sentiment = "neutral"
        next_action = "保留线索，后续用更温和方式继续跟进。"
    else:
        sentiment = "mixed" if "担心" in prompt or "怕被坑" in prompt else "neutral"
        next_action = "根据客户意向继续沟通，并补充关键房源信息。"

    key_points = []
    if "价格" in prompt or "房租" in prompt:
        key_points.append("客户关注租金和价格相关信息。")
    if "押金" in prompt or "中介费" in prompt:
        key_points.append("客户关注押金、中介费和隐形收费。")
    if "带看" in prompt or "实地看看房" in prompt:
        key_points.append("客户已经表现出看房意向。")
    if "别再给我打电话" in prompt:
        key_points.append("客户明确表示拒绝继续被联系。")
    if not key_points:
        key_points.append("客户表达了基础咨询需求，需要进一步识别意向。")

    response: dict[str, Any] = {
        "summary": "这是一通关于租房房源咨询的客服通话，系统已提取客户态度和后续建议。",
        "sentiment": sentiment,
        "follow_up_needed": follow_up_needed and "negative" not in lowered_prompt,
        "key_points": key_points,
        "next_action": next_action,
    }
    return json.dumps(response, ensure_ascii=False)


def call_llm(prompt: str) -> str:
    if settings.use_mock_llm:
        return _build_mock_response(prompt)

    from litellm import completion

    response = completion(
        model=settings.litellm_model,
        messages=[
            {
                "role": "system",
                "content": "你是一个客服通话分析助手。必须只输出合法 JSON，禁止输出额外解释。",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or ""
