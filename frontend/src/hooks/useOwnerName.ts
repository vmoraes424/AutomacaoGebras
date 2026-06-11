import { useEffect, useState } from "react";
import { api, peekApiCache } from "../api/client";

/** Resposta < 4s indica hit no cache backend; miss no Pipedrive leva ~15s+. */
const BACKEND_CACHE_HIT_MS = 4000;

/** Resolve nome do consultor — usa state da rota ou busca em /pipedrive/users. */
export function useOwnerName(ownerUserId: number | undefined, ownerNameFromNav: string): string {
  const [resolved, setResolved] = useState(ownerNameFromNav);

  useEffect(() => {
    if (ownerNameFromNav) {
      setResolved(ownerNameFromNav);
      return;
    }
    if (!ownerUserId || Number.isNaN(ownerUserId)) {
      setResolved("");
      return;
    }

    const cached = peekApiCache<{ id: number; name: string }[]>("/pipedrive/users");
    const cachedMatch = cached?.find((u) => u.id === ownerUserId);
    if (cachedMatch) {
      setResolved(cachedMatch.name ?? "");
      return;
    }

    let cancelled = false;

    async function resolveName() {
      try {
        const t0 = performance.now();
        const users = await api.listUsers({ fresh: false });
        const elapsed = performance.now() - t0;
        if (cancelled) return;

        const match = users.find((u) => u.id === ownerUserId);
        setResolved(match?.name ?? "");

        if (elapsed < BACKEND_CACHE_HIT_MS) {
          const freshUsers = await api.listUsers({ fresh: true });
          if (cancelled) return;
          const freshMatch = freshUsers.find((u) => u.id === ownerUserId);
          setResolved(freshMatch?.name ?? "");
        }
      } catch {
        if (!cancelled) setResolved("");
      }
    }

    void resolveName();

    return () => {
      cancelled = true;
    };
  }, [ownerUserId, ownerNameFromNav]);

  return resolved;
}
