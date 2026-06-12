import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { PipedriveFieldOption } from "../api/types";

export function usePipeFieldOptions(): {
  options: Record<string, PipedriveFieldOption[]>;
  loading: boolean;
} {
  const [options, setOptions] = useState<Record<string, PipedriveFieldOption[]>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .getDealFieldOptions()
      .then((res) => {
        if (!cancelled) setOptions(res.fields ?? {});
      })
      .catch(() => {
        if (!cancelled) setOptions({});
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return { options, loading };
}
