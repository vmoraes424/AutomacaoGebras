"""Cache TTL curto + single-flight — uma leitura Pipe por vez, reutilizada no TTL."""

from __future__ import annotations

import threading
import time
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class TtlSingleflightCache(Generic[T]):
    """
    - fresh=False: devolve valor em cache se ainda dentro do TTL.
    - fresh=True: ignora cache e busca de novo.
    - Requisições concorrentes compartilham a mesma chamada em andamento.
    """

    def __init__(self, ttl_seconds: float = 30.0) -> None:
        self._ttl = ttl_seconds
        self._lock = threading.Lock()
        self._value: T | None = None
        self._expires_at: float = 0.0
        self._inflight: threading.Event | None = None
        self._inflight_error: BaseException | None = None

    def get_or_fetch(self, *, fresh: bool, fetcher: Callable[[], T]) -> T:
        if not fresh:
            with self._lock:
                if self._value is not None and time.monotonic() < self._expires_at:
                    return self._value

        with self._lock:
            if not fresh and self._value is not None and time.monotonic() < self._expires_at:
                return self._value

            if self._inflight is not None:
                waiter = self._inflight
                is_leader = False
            else:
                waiter = None
                is_leader = True
                self._inflight = threading.Event()
                self._inflight_error = None

        if not is_leader:
            assert waiter is not None
            waiter.wait()
            with self._lock:
                if self._inflight_error is not None:
                    raise self._inflight_error
                assert self._value is not None
                return self._value

        try:
            result = fetcher()
        except BaseException as exc:
            with self._lock:
                self._inflight_error = exc
                event = self._inflight
                self._inflight = None
            event.set()
            raise

        with self._lock:
            self._value = result
            self._expires_at = time.monotonic() + self._ttl
            event = self._inflight
            self._inflight = None
        event.set()
        return result

    def invalidate(self) -> None:
        with self._lock:
            self._value = None
            self._expires_at = 0.0
