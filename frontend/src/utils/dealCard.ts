import type { CrmDeal, OperationalLabel } from "../api/types";
import { formatDisplayName } from "./formatDisplayName";

export const DEAL_LABEL_TEXT: Record<OperationalLabel, string> = {
  pendente: "Pendente",
  rascunho: "Rascunho",
  erro: "Erro de validação",
  enviado: "Enviado",
  processando: "Processando",
  processado: "Processado",
};

export function dealOperationalLabel(deal: CrmDeal): OperationalLabel {
  return deal.operational_label ?? "pendente";
}

export function dealDisplayTitle(deal: CrmDeal): string {
  return formatDisplayName(deal.title);
}

export function dealDisplayCliente(deal: CrmDeal): string | null {
  if (!deal.cliente?.trim()) return null;
  const cliente = formatDisplayName(deal.cliente);
  const titleNorm = deal.title.trim().toLowerCase();
  if (cliente.trim().toLowerCase() === titleNorm) return null;
  return cliente;
}

export function dealFormButtonLabel(label: OperationalLabel): string {
  if (label === "enviado" || label === "processando" || label === "processado") {
    return "Ver formulário";
  }
  return "Preencher formulário";
}

/** Espelha portal/domain/formulario/operational.py — badge no formulário. */
export function formStatusToOperationalLabel(formStatus: string): OperationalLabel {
  switch (formStatus) {
    case "draft":
      return "rascunho";
    case "error":
      return "erro";
    case "validated":
    case "submitted":
      return "enviado";
    case "processing":
      return "processando";
    case "processed":
      return "processado";
    default:
      return "pendente";
  }
}
