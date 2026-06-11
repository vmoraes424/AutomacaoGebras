import { renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useCrmQuery } from "../hooks/useCrmQuery";

describe("useCrmQuery", () => {
  it("carrega dados com uma única chamada ao fetcher", async () => {
    const fetcher = vi.fn(async () => ["a"]);

    const { result } = renderHook(({ key }) => useCrmQuery(key, fetcher, [] as string[]), {
      initialProps: { key: "/test" },
    });

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.data).toEqual(["a"]);
    expect(fetcher).toHaveBeenCalledTimes(1);
  });

  it("propaga erro do fetcher", async () => {
    const fetcher = vi.fn(async () => {
      throw new Error("falhou");
    });

    const { result } = renderHook(() => useCrmQuery("/err", fetcher, [] as string[]));

    await waitFor(() => expect(result.current.error).toBe("falhou"));
    expect(result.current.loading).toBe(false);
  });
});
