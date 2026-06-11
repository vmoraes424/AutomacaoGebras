"""Testes cache TTL + single-flight."""

from __future__ import annotations

import threading
import time

from portal.infrastructure.cache.ttl_singleflight import TtlSingleflightCache


def test_ttl_cache_reutiliza_sem_fresh():
    cache: TtlSingleflightCache[int] = TtlSingleflightCache(ttl_seconds=15.0)
    calls = {"n": 0}

    def fetcher() -> int:
        calls["n"] += 1
        return 42

    assert cache.get_or_fetch(fresh=False, fetcher=fetcher) == 42
    assert cache.get_or_fetch(fresh=False, fetcher=fetcher) == 42
    assert calls["n"] == 1


def test_fresh_ignora_ttl():
    cache: TtlSingleflightCache[int] = TtlSingleflightCache(ttl_seconds=60.0)
    calls = {"n": 0}

    def fetcher() -> int:
        calls["n"] += 1
        return calls["n"]

    assert cache.get_or_fetch(fresh=True, fetcher=fetcher) == 1
    assert cache.get_or_fetch(fresh=True, fetcher=fetcher) == 2
    assert calls["n"] == 2


def test_singleflight_paralelo():
    cache: TtlSingleflightCache[int] = TtlSingleflightCache(ttl_seconds=15.0)
    calls = {"n": 0}

    def fetcher() -> int:
        calls["n"] += 1
        time.sleep(0.05)
        return 7

    results: list[int] = []

    def worker() -> None:
        results.append(cache.get_or_fetch(fresh=True, fetcher=fetcher))

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert results == [7, 7]
    assert calls["n"] == 1


def test_fresh_true_nao_reutiliza_cache_valido():
    cache: TtlSingleflightCache[int] = TtlSingleflightCache(ttl_seconds=60.0)
    calls = {"n": 0}

    def fetcher() -> int:
        calls["n"] += 1
        return calls["n"]

    assert cache.get_or_fetch(fresh=False, fetcher=fetcher) == 1
    assert cache.get_or_fetch(fresh=True, fetcher=fetcher) == 2
    assert calls["n"] == 2


def test_invalidate_forca_nova_leitura():
    cache: TtlSingleflightCache[int] = TtlSingleflightCache(ttl_seconds=60.0)
    calls = {"n": 0}

    def fetcher() -> int:
        calls["n"] += 1
        return calls["n"]

    assert cache.get_or_fetch(fresh=False, fetcher=fetcher) == 1
    cache.invalidate()
    assert cache.get_or_fetch(fresh=False, fetcher=fetcher) == 2
    assert calls["n"] == 2

