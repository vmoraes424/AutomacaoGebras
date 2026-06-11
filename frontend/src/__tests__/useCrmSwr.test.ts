import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useCrmSwr } from "../hooks/useCrmSwr";
import { resetApiClientCachesForTests } from "../api/client";

describe("useCrmSwr", () => {
  beforeEach(() => {
    resetApiClientCachesForTests();
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });

  it("revalida em background quando há cache client", async () => {
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce(["stale"])
      .mockResolvedValueOnce(["fresh"]);

    const { result, rerender } = renderHook(
      ({ key }) => useCrmSwr(key, fetcher, [] as string[]),
      { initialProps: { key: "/test" } },
    );

    await waitFor(() => expect(fetcher).toHaveBeenCalledWith({ fresh: false }));
    fetcher.mockClear();

    await fetcher({ fresh: false });
    resetApiClientCachesForTests();
    await fetcher({ fresh: false });

    rerender({ key: "/test" });
  });

  it("não revalida fresh quando miss lento (dados já frescos)", async () => {
    vi.useRealTimers();
    const originalNow = performance.now.bind(performance);
    let fakeNow = 0;
    performance.now = () => fakeNow;

    const fetcher = vi.fn(async (opts?: { fresh?: boolean }) => {
      if (!opts?.fresh) {
        fakeNow += 5000;
        return ["from-pipe"];
      }
      return ["should-not-call"];
    });

    const { result } = renderHook(() =>
      useCrmSwr("/slow", fetcher, [] as string[]),
    );

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.data).toEqual(["from-pipe"]);
    expect(fetcher).toHaveBeenCalledTimes(1);
    expect(fetcher).toHaveBeenCalledWith({ fresh: false });

    performance.now = originalNow;
  });

  it("revalida fresh após hit rápido no backend", async () => {
    const fetcher = vi
      .fn()
      .mockImplementation(async (opts?: { fresh?: boolean }) =>
        opts?.fresh ? ["fresh"] : ["cached"],
      );

    const { result } = renderHook(() =>
      useCrmSwr("/fast", fetcher, [] as string[]),
    );

    await waitFor(() => expect(result.current.data).toEqual(["fresh"]));
    expect(fetcher).toHaveBeenCalledWith({ fresh: false });
    expect(fetcher).toHaveBeenCalledWith({ fresh: true });
  });
});
