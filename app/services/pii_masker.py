import re


PHONE_PATTERN = re.compile(r"1[3-9]\d{9}")
EMAIL_PATTERN = re.compile(r"([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")


def mask_phone(text: str) -> str:
    return PHONE_PATTERN.sub(lambda match: f"{match.group(0)[:3]}****{match.group(0)[-4:]}", text)


def mask_email(text: str) -> str:
    return EMAIL_PATTERN.sub(lambda match: f"{match.group(1)}***@{match.group(2)}", text)


def mask_text(text: str) -> str:
    masked_text = mask_phone(text)
    masked_text = mask_email(masked_text)
    return masked_text
