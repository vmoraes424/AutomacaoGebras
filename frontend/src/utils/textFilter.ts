export function normalizeFilterText(value: string): string {
  return value
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase()
    .trim();
}

export function textIncludesFilter(haystack: string, filter: string): boolean {
  if (!filter) return true;
  const q = normalizeFilterText(filter);
  if (!q) return true;
  return normalizeFilterText(haystack).includes(q);
}
