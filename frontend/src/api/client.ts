import type {
  CrmDeal,
  CrmUser,
  AutomacaoConfig,
  FormAttachmentsMeta,
  FormDraftBody,
  FormReadiness,
  FormRecord,
  HubInstalacoesResponse,
  HubServicosResponse,
  PipedriveDealFieldOptions,
} from "./types";
import {
  fetchWithApiCache,
  hasApiCache,
  invalidateApiCache,
  peekApiCache,
  resetApiClientCachesForTests as resetRequestCacheForTests,
} from "./requestCache";
import { configAuthHeaders } from "../utils/configAuth";

export { hasApiCache, peekApiCache, invalidateApiCache };

export function resetApiClientCachesForTests(): void {
  resetRequestCacheForTests();
  inflightGetForm.clear();
}

async function configRequest<T>(path: string, init?: RequestInit): Promise<T> {
  return request<T>(path, {
    ...init,
    headers: {
      ...(init?.headers as Record<string, string> | undefined),
      ...configAuthHeaders(),
    },
  });
}

const API_BASE = import.meta.env.VITE_API_URL ?? "";

const PIPE_FIELD_OPTIONS_TTL_MS = 30 * 60 * 1000;

const inflightGetForm = new Map<string, Promise<FormRecord>>();

async function request<T>(path: string, init?: RequestInit & { fresh?: boolean }): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers as Record<string, string> | undefined),
  };
  if (init?.fresh) {
    headers["X-Portal-Fresh"] = "1";
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  });
  const contentType = response.headers?.get?.("content-type") ?? "";

  if (!response.ok) {
    const body = contentType.includes("application/json")
      ? await response.json().catch(() => ({}))
      : {};
    const detail = (body as { detail?: string }).detail ?? response.statusText;
    throw new Error(detail || `HTTP ${response.status}`);
  }

  if (contentType.includes("text/html")) {
    throw new Error(
      `Resposta inválida da API (${response.status}). Verifique o proxy do Vite ou VITE_API_URL (rota ${path}).`,
    );
  }

  return response.json() as Promise<T>;
}

function cacheKey(path: string) {
  return path;
}

export const api = {
  listUsers: () =>
    fetchWithApiCache(cacheKey("/pipedrive/users"), () =>
      request<CrmUser[]>("/pipedrive/users"),
    ),

  listDeals: (ownerUserId: number) =>
    fetchWithApiCache(cacheKey(`/pipedrive/deals?owner_user_id=${ownerUserId}`), () =>
      request<CrmDeal[]>(`/pipedrive/deals?owner_user_id=${ownerUserId}`),
    ),

  getDealFieldOptions: () =>
    fetchWithApiCache(
      cacheKey("/pipedrive/deal-field-options"),
      async () => {
        const headers: Record<string, string> = { "Content-Type": "application/json" };
        const response = await fetch(`${API_BASE}/pipedrive/deal-field-options`, { headers });
        if (response.status === 404) {
          throw new Error(
            "Backend desatualizado: a rota GET /pipedrive/deal-field-options não existe. " +
              "No PC do servidor rode git pull, reinicie uvicorn portal.main:app e teste " +
              "http://localhost:8000/pipedrive/deal-field-options",
          );
        }
        if (!response.ok) {
          const body = await response.json().catch(() => ({}));
          const detail = (body as { detail?: string }).detail ?? response.statusText;
          throw new Error(detail || `HTTP ${response.status}`);
        }
        return response.json() as Promise<PipedriveDealFieldOptions>;
      },
      { maxAgeMs: PIPE_FIELD_OPTIONS_TTL_MS },
    ),

  getHubServicos: () =>
    fetchWithApiCache(cacheKey("/hub/servicos"), () =>
      request<HubServicosResponse>("/hub/servicos"),
    ),

  getHubInstalacoes: (codigoClienteInstalacao: string) =>
    request<HubInstalacoesResponse>(
      `/hub/instalacoes?${new URLSearchParams({
        codigo_cliente_instalacao: codigoClienteInstalacao,
      })}`,
    ),

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

  saveDraft: (dealId: number, body: FormDraftBody) => {
    invalidateApiCache("/pipedrive/deals");
    return request<FormRecord>(`/forms/${dealId}/draft`, {
      method: "PUT",
      body: JSON.stringify(body),
    });
  },

  getFormReadiness: (dealId: number, body: FormDraftBody) =>
    request<FormReadiness>(`/forms/${dealId}/readiness`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  getFormAttachments: (dealId: number) =>
    fetchWithApiCache(cacheKey(`/forms/${dealId}/attachments`), () =>
      request<FormAttachmentsMeta>(`/forms/${dealId}/attachments`),
    ),

  submitForm: (dealId: number, body: FormDraftBody) => {
    invalidateApiCache("/pipedrive/deals");
    return request<FormRecord>(`/forms/${dealId}/submit`, {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

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
  getAutomacaoConfigAccess: () =>
    request<{ password_required: boolean }>("/config/automacao/access"),

  getAutomacaoConfig: () => configRequest<AutomacaoConfig>("/config/automacao"),

  saveAutomacaoConfig: (body: AutomacaoConfig) =>
    configRequest<AutomacaoConfig>("/config/automacao", {
      method: "PUT",
      body: JSON.stringify(body),
    }),

  applyAutomacaoDevPreset: () =>
    configRequest<AutomacaoConfig>("/config/automacao/preset/dev", { method: "POST" }),

  applyAutomacaoProdPreset: () =>
    configRequest<AutomacaoConfig>("/config/automacao/preset/prod", { method: "POST" }),
};
