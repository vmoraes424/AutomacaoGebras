import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { api, invalidateApiCache, peekApiCache } from "../api/client";
import type { PipedriveDealFieldOptions, PipedriveFieldOption } from "../api/types";

export const PIPE_FIELD_OPTIONS_CACHE_KEY = "/pipedrive/deal-field-options";

type PipeFieldOptionsContextValue = {
  options: Record<string, PipedriveFieldOption[]>;
  loading: boolean;
  error: string;
};

const PipeFieldOptionsContext = createContext<PipeFieldOptionsContextValue>({
  options: {},
  loading: true,
  error: "",
});

/** Catálogo global de selects do Pipedrive — uma carga por sessão do portal. */
export function PipeFieldOptionsProvider({ children }: { children: ReactNode }) {
  const cached = peekApiCache<PipedriveDealFieldOptions>(PIPE_FIELD_OPTIONS_CACHE_KEY);
  const [options, setOptions] = useState<Record<string, PipedriveFieldOption[]>>(
    () => cached?.fields ?? {},
  );
  const [loading, setLoading] = useState(() => cached === null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    invalidateApiCache(PIPE_FIELD_OPTIONS_CACHE_KEY);
    setLoading(true);

    api
      .getDealFieldOptions({ fresh: true })
      .then((res) => {
        if (!cancelled) setOptions(res.fields ?? {});
      })
      .catch((e) => {
        if (!cancelled) {
          setOptions({});
          setError(e instanceof Error ? e.message : String(e));
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <PipeFieldOptionsContext.Provider value={{ options, loading, error }}>
      {children}
    </PipeFieldOptionsContext.Provider>
  );
}

export function usePipeFieldOptions(): PipeFieldOptionsContextValue {
  return useContext(PipeFieldOptionsContext);
}
