import threading
import time


class TokenBucket:
    def __init__(self, rate_per_second: float, capacity: float | None = None) -> None:
        if rate_per_second <= 0:
            raise ValueError(
                f"rate_per_second must be positive, got {rate_per_second!r}"
            )
        self._rate = float(rate_per_second)
        # A bigger bucket banks tokens while idle, then exceeds the rate in 1s.
        self._capacity = float(capacity) if capacity is not None else 1.0
        self._tokens = 0.0
        self._updated = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self, tokens: float = 1.0) -> None:
        while True:
            with self._lock:
                now = time.monotonic()
                self._tokens = min(
                    self._capacity, self._tokens + (now - self._updated) * self._rate
                )
                self._updated = now
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                wait = (tokens - self._tokens) / self._rate
            time.sleep(wait)
