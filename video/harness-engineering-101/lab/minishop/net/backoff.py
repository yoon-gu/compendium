"""Exponential backoff shared by every outbound client."""
import random
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    attempts: int = 3          # total tries, including the first one
    base_delay: float = 0.25   # seconds before the 2nd try; doubles each time
    max_delay: float = 10.0
    jitter: float = 0.1        # +/- 10% so clients don't retry in lockstep


def policy_from(cfg):
    """Build a policy from a settings dict such as settings.PAYMENT_HTTP."""
    return RetryPolicy(attempts=cfg.get("attempts", 3), base_delay=cfg.get("base_delay", 0.25),
                       max_delay=cfg.get("max_delay", 10.0))


def delays(policy):
    """Sleep lengths between tries: base, 2*base, 4*base ... capped at max_delay."""
    d = policy.base_delay
    for _ in range(policy.attempts - 1):
        yield min(d, policy.max_delay)
        d *= 2


def with_backoff(policy, fn, *args, retry_if=lambda e: getattr(e, "retryable", False), **kwargs):
    last = None
    waits = list(delays(policy)) + [None]
    for wait in waits:
        try:
            return fn(*args, **kwargs)
        except Exception as e:  # noqa: BLE001
            if not retry_if(e) or wait is None:
                raise
            last = e
            time.sleep(wait * random.uniform(1 - policy.jitter, 1 + policy.jitter))
    raise last
