import React, { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react';
import { cn } from '../../@/lib/utils';

export type ToastType = 'success' | 'error' | 'info';

interface ToastItem {
  id: number;
  message: string;
  type: ToastType;
}

interface ToastContextType {
  /** Shows a toast at app level, so it survives the dialog or drawer that raised it closing. */
  showToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

const DURATION_MS: Record<ToastType, number> = { success: 3500, info: 5000, error: 6000 };
const MAX_VISIBLE = 3;

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const nextId = useRef(0);
  const timers = useRef(new Map<number, ReturnType<typeof setTimeout>>());

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
    const timer = timers.current.get(id);
    if (timer) clearTimeout(timer);
    timers.current.delete(id);
  }, []);

  const showToast = useCallback(
    (message: string, type: ToastType = 'success') => {
      const id = ++nextId.current;
      setToasts((prev) => [...prev.filter((t) => t.message !== message), { id, message, type }].slice(-MAX_VISIBLE));
      timers.current.set(id, setTimeout(() => dismiss(id), DURATION_MS[type]));
    },
    [dismiss],
  );

  useEffect(() => {
    const pending = timers.current;
    return () => pending.forEach((timer) => clearTimeout(timer));
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div className="fixed bottom-5 right-5 z-[100] flex flex-col items-end gap-2" role="status" aria-live="polite">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={cn(
              'flex items-center gap-2.5 px-4 py-2.5 rounded-lg text-xs font-semibold shadow-2xl border animate-in fade-in slide-in-from-bottom-5 duration-200 select-none',
              toast.type === 'error' ? 'bg-red-900 text-white border-red-500/50' : 'bg-[#00205B] text-white border-emerald-500/50',
            )}
          >
            {toast.type === 'success' && <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />}
            {toast.type === 'error' && <AlertCircle className="h-4 w-4 text-red-400 shrink-0" />}
            {toast.type === 'info' && <Info className="h-4 w-4 text-sky-300 shrink-0" />}
            <span>{toast.message}</span>
            <button
              type="button"
              aria-label="Dismiss notification"
              onClick={() => dismiss(toast.id)}
              className="ml-2 text-slate-400 hover:text-white cursor-pointer transition-colors"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = (): ToastContextType => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};
