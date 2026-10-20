import type { AuthSession } from "../types/api";

const storageKey = "logsight.session";

// This demo stores the short-lived JWT in sessionStorage so closing the browser clears it.
export const auth = {
  get: (): AuthSession | null => { try { const value = sessionStorage.getItem(storageKey); return value ? JSON.parse(value) as AuthSession : null; } catch { return null; } },
  set: (session: AuthSession) => sessionStorage.setItem(storageKey, JSON.stringify(session)),
  clear: () => sessionStorage.removeItem(storageKey),
};
