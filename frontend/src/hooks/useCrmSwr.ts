import { useEffect, useRef, useState } from "react";
import { hasApiCache, peekApiCache } from "../api/client";

/** Resposta < 4s indica hit no cache backend (~1s); miss no Pipedrive leva ~15s+. */
const BACKEND_CACHE_HIT_MS = 4000;

type Fetcher<T> = (opts: { fresh?: boolean }) => Promise<T>;

/**
 * SWR para listas CRM: placeholder instantâneo + revalidação sem bloquear UI.
 * - Cache client: mostra na hora, revalida fresh=true em background.
 * - Sem cache client: fresh=false primeiro (backend TTL ~1s); se hit, revalida fresh=true.
 * - Miss lento no Pipedrive: dados já frescos, não dispara segunda chamada.
 */
export function useCrmSwr<T>(cacheKey: string, fetcher: Fetcher<T>, initial: T) {
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const [data, setData] = useState<T>(() => peekApiCache<T>(cacheKey) ?? initial);
  const [loading, setLoading] = useState(() => !hasApiCache(cacheKey));
  const [error, setError] = useState("");

  useEffect(() => {
    if (!cacheKey) return;

    let cancelled = false;
    const hadClientCache = hasApiCache(cacheKey);
    const load = fetcherRef.current;

    async function run() {
      try {
        if (hadClientCache) {
          const fresh = await load({ fresh: true });
          if (!cancelled) setData(fresh);
          return;
        }

        const t0 = performance.now();
        const initialData = await load({ fresh: false });
        const elapsed = performance.now() - t0;

        if (!cancelled) {
          setData(initialData);
          setLoading(false);
        }

        if (elapsed < BACKEND_CACHE_HIT_MS) {
          const fresh = await load({ fresh: true });
          if (!cancelled) setData(fresh);
        }
      } catch (e) {
        if (!cancelled) setError((e as Error).message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void run();
    return () => {
      cancelled = true;
    };
  }, [cacheKey]);

  return { data, loading, error };
}
