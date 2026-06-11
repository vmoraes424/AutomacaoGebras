const STORAGE_KEY = "portal_config_password";

export function getStoredConfigPassword(): string {
  try {
    return sessionStorage.getItem(STORAGE_KEY) ?? "";
  } catch {
    return "";
  }
}

export function setStoredConfigPassword(password: string): void {
  try {
    if (password) {
      sessionStorage.setItem(STORAGE_KEY, password);
    } else {
      sessionStorage.removeItem(STORAGE_KEY);
    }
  } catch {
    /* ignore */
  }
}

export function clearStoredConfigPassword(): void {
  setStoredConfigPassword("");
}

export function configAuthHeaders(): Record<string, string> {
  const password = getStoredConfigPassword();
  return password ? { "X-Portal-Config-Password": password } : {};
}
