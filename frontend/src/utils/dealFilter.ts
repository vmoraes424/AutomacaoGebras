import type { CrmDeal } from "../api/types";
import { normalizeFilterText, textIncludesFilter } from "./textFilter";

export function matchesDealFilter(deal: CrmDeal, filter: string): boolean {
  if (!filter.trim()) return true;

  const digits = normalizeFilterText(filter).replace(/\D/g, "");
  if (digits && String(deal.id).includes(digits)) return true;
  if (textIncludesFilter(String(deal.id), filter)) return true;
  if (textIncludesFilter(deal.title, filter)) return true;
  if (deal.cliente && textIncludesFilter(deal.cliente, filter)) return true;
  return false;
}
