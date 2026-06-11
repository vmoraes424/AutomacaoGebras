import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  fetchWithApiCache,
  invalidateApiCache,
  peekApiCache,
  resetApiClientCachesForTests,
} from "../api/requestCache";

describe("requestCache", () => {
  beforeEach(() => {
    resetApiClientCachesForTests();
  });

  it("reutiliza cache dentro do TTL", async () => {
    const fetcher = vi.fn(async () => ["x"]);
    await fetchWithApiCache("k", fetcher);
    await fetchWithApiCache("k", fetcher);
    expect(fetcher).toHaveBeenCalledTimes(1);
  });

  it("deduplica requisições concorrentes", async () => {
    const fetcher = vi.fn(
      () =>
        new Promise<string[]>((resolve) => {
          setTimeout(() => resolve(["x"]), 20);
        }),
    );
    const p1 = fetchWithApiCache("k", fetcher);
    const p2 = fetchWithApiCache("k", fetcher);
    expect(await p1).toEqual(["x"]);
    expect(await p2).toEqual(["x"]);
    expect(fetcher).toHaveBeenCalledTimes(1);
  });

  it("invalidateApiCache limpa por prefixo", async () => {
    await fetchWithApiCache("/pipedrive/users", async () => [1]);
    invalidateApiCache("/pipedrive");
    expect(peekApiCache("/pipedrive/users")).toBeNull();
  });
});
