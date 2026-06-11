import { useCallback, useState } from "react";

export type SyncToastItem = {
  id: string;
  title: string;
  message: string;
};

const AUTO_DISMISS_MS = 7000;

export function useSyncToasts() {
  const [toasts, setToasts] = useState<SyncToastItem[]>([]);

  const addToast = useCallback((title: string, message: string) => {
    const id = crypto.randomUUID();
    setToasts((prev) => [...prev, { id, title, message }]);
    window.setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, AUTO_DISMISS_MS);
  }, []);

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return { toasts, addToast, dismiss };
}

type SyncToastStackProps = {
  toasts: SyncToastItem[];
  onDismiss: (id: string) => void;
};

export function SyncToastStack({ toasts, onDismiss }: SyncToastStackProps) {
  if (toasts.length === 0) return null;

  return (
    <div className="toast-stack" aria-live="polite" aria-relevant="additions">
      {toasts.map((toast) => (
        <div key={toast.id} className="sync-toast" role="alert">
          <div className="sync-toast-body">
            <strong className="sync-toast-title">{toast.title}</strong>
            <p className="sync-toast-message">{toast.message}</p>
          </div>
          <button
            type="button"
            className="sync-toast-close"
            aria-label="Fechar"
            onClick={() => onDismiss(toast.id)}
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
}
