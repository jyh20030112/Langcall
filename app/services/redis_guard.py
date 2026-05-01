from dataclasses import dataclass
from uuid import uuid4

from redis.lock import Lock

from app.core.config import settings
from app.core.redis_client import get_redis_client


@dataclass
class RedisGuardResult:
    acquired: bool
    token: str

# 防止同一个 call_id 重复排队
def try_acquire_webhook_guard(call_id: str) -> RedisGuardResult:
    client = get_redis_client()
    key = f"idem:webhook:{call_id}"
    token = str(uuid4())
    acquired = bool(    # 判断锁是否成功获取
        client.set(
            key,
            token,
            ex=settings.webhook_idempotency_ttl_seconds,
            nx=True,
        )
    )
    return RedisGuardResult(acquired=acquired, token=token)


def release_webhook_guard(call_id: str, token: str) -> None:
    client = get_redis_client()
    key = f"idem:webhook:{call_id}"
    current_token = client.get(key)
    if current_token == token:
        client.delete(key)

# 防止多个 Worker 并发处理同一条通话
def build_call_processing_lock(call_id: str) -> Lock:
    client = get_redis_client()
    return client.lock(
        name=f"lock:call:{call_id}",
        timeout=settings.call_processing_lock_ttl_seconds,
        blocking=False,
    )
