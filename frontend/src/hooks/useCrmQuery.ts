import { useEffect, useRef, useState } from "react";
import { peekApiCache } from "../api/client";

/** Uma requisição por cacheKey; reutiliza cache client se disponível. */
export function useCrmQuery<T>(cacheKey: string, fetcher: () => Promise<T>, initial: T) {
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const [data, setData] = useState<T>(() => peekApiCache<T>(cacheKey) ?? initial);
  const [loading, setLoading] = useState(() => peekApiCache<T>(cacheKey) === null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!cacheKey) return;

    let cancelled = false;
    setLoading(peekApiCache<T>(cacheKey) === null);
    setError("");

    fetcherRef
      .current()
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [cacheKey]);

  return { data, loading, error };
}
