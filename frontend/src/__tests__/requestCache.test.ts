import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  fetchWithApiCache,
  hasApiCache,
  invalidateApiCache,
  peekApiCache,
  resetApiClientCachesForTests,
} from "../api/requestCache";

describe("requestCache", () => {
  beforeEach(() => {
    resetApiClientCachesForTests();
    vi.useFakeTimers();
  });

  it("revalida com fresh=true mesmo com cache recente", async () => {
    let n = 0;
    const fetcher = vi.fn(async () => {
      n += 1;
      return n;
    });

    await fetchWithApiCache("k", fetcher, { fresh: true });
    await fetchWithApiCache("k", fetcher, { fresh: true });
    expect(fetcher).toHaveBeenCalledTimes(2);
  });

  it("reutiliza cache com fresh=false", async () => {
    const fetcher = vi.fn(async () => ["a"]);

    await fetchWithApiCache("k", fetcher, { fresh: true });
    await fetchWithApiCache("k", fetcher, { fresh: false });
    expect(fetcher).toHaveBeenCalledTimes(1);
    expect(peekApiCache<string[]>("k")).toEqual(["a"]);
  });

  it("hasApiCache detecta array vazio como cache válido", async () => {
    await fetchWithApiCache("k", async () => [], { fresh: true });
    expect(hasApiCache("k")).toBe(true);
    expect(peekApiCache<string[]>("k")).toEqual([]);
  });

  it("escrita stale não sobrescreve cache fresh", async () => {
    let freshN = 0;
    let staleN = 0;

    await fetchWithApiCache(
      "k",
      async () => {
        freshN += 1;
        return ["fresh"];
      },
      { fresh: true },
    );

    await fetchWithApiCache(
      "k",
      async () => {
        staleN += 1;
        return ["stale"];
      },
      { fresh: false },
    );

    expect(freshN).toBe(1);
    expect(staleN).toBe(0);
    expect(peekApiCache<string[]>("k")).toEqual(["fresh"]);
  });

  it("fresh=true não compartilha inflight com fresh=false", async () => {
    let resolveStale: (value: string[]) => void;
    const stalePromise = new Promise<string[]>((resolve) => {
      resolveStale = resolve;
    });
    const staleFetcher = vi.fn(() => stalePromise);
    const freshFetcher = vi.fn(async () => ["fresh"]);

    const staleInflight = fetchWithApiCache("k", staleFetcher, { fresh: false });
    const freshInflight = fetchWithApiCache("k", freshFetcher, { fresh: true });

    resolveStale!(["stale"]);
    expect(await staleInflight).toEqual(["stale"]);
    expect(await freshInflight).toEqual(["fresh"]);
    expect(staleFetcher).toHaveBeenCalledTimes(1);
    expect(freshFetcher).toHaveBeenCalledTimes(1);
    expect(peekApiCache<string[]>("k")).toEqual(["fresh"]);
  });

  it("invalidate limpa prefixo", async () => {
    await fetchWithApiCache("/pipedrive/users", async () => [1], { fresh: true });
    invalidateApiCache("/pipedrive");
    expect(peekApiCache("/pipedrive/users")).toBeNull();
    expect(hasApiCache("/pipedrive/users")).toBe(false);
  });
});
