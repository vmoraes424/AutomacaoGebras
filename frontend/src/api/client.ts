import type { CrmDeal, CrmUser, FormDraftBody, FormRecord } from "./types";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

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
    return request<FormRecord>(`/forms/${dealId}${qs ? `?${qs}` : ""}`);
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
};
