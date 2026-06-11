import { useEffect, useState } from "react";
import { api, peekApiCache } from "../api/client";

/** Resolve nome do consultor — usa state da rota ou cache de /pipedrive/users. */
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

    api
      .listUsers()
      .then((users) => {
        if (cancelled) return;
        const match = users.find((u) => u.id === ownerUserId);
        setResolved(match?.name ?? "");
      })
      .catch(() => {
        if (!cancelled) setResolved("");
      });

    return () => {
      cancelled = true;
    };
  }, [ownerUserId, ownerNameFromNav]);

  return resolved;
}
