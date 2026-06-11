import type { CrmDeal, CrmUser, FormDraftBody, FormRecord } from "./types";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

const inflightGetForm = new Map<string, Promise<FormRecord>>();

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = (body as { detail?: string }).detail ?? response.statusText;
    throw new Error(detail || `HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  listUsers: () => request<CrmUser[]>("/pipedrive/users"),

  listDeals: (ownerUserId: number) =>
    request<CrmDeal[]>(`/pipedrive/deals?owner_user_id=${ownerUserId}`),

  getForm: (
    dealId: number,
    opts?: { ownerUserId?: number; ownerName?: string; dealTitle?: string },
  ) => {
    const params = new URLSearchParams();
    if (opts?.ownerUserId != null) params.set("owner_user_id", String(opts.ownerUserId));
    if (opts?.ownerName) params.set("owner_name", opts.ownerName);
    if (opts?.dealTitle) params.set("deal_title", opts.dealTitle);
    const qs = params.toString();
    const path = `/forms/${dealId}${qs ? `?${qs}` : ""}`;
    const inflight = inflightGetForm.get(path);
    if (inflight) return inflight;
    const promise = request<FormRecord>(path).finally(() => {
      inflightGetForm.delete(path);
    });
    inflightGetForm.set(path, promise);
    return promise;
  },

  saveDraft: (dealId: number, body: FormDraftBody) =>
    request<FormRecord>(`/forms/${dealId}/draft`, {
      method: "PUT",
      body: JSON.stringify(body),
    }),

  submitForm: (dealId: number, body: FormDraftBody) =>
    request<FormRecord>(`/forms/${dealId}/submit`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  syncToPipedrive: (dealId: number, body: FormDraftBody) =>
    request<{ deal_id: number; synced: boolean; message: string }>(
      `/forms/${dealId}/sync-pipedrive`,
      {
        method: "POST",
        body: JSON.stringify(body),
      },
    ),

  syncFieldToPipedrive: (
    dealId: number,
    fieldPath: string,
    value: string | number,
    meta?: Pick<FormDraftBody, "owner_user_id" | "owner_name" | "deal_title" | "schema_version">,
  ) =>
    request<{ deal_id: number; field_path: string; synced: boolean; skipped?: boolean }>(
      `/forms/${dealId}/sync-field`,
      {
        method: "POST",
        body: JSON.stringify({
          field_path: fieldPath,
          value,
          schema_version: meta?.schema_version ?? "v1",
          owner_user_id: meta?.owner_user_id,
          owner_name: meta?.owner_name ?? "",
          deal_title: meta?.deal_title ?? "",
        }),
      },
    ),
};
