import type { PropsWithChildren } from 'react';

interface ModalProps extends PropsWithChildren {
  open: boolean;
  onClose: () => void;
  title: string;
}

export function Modal({ children, open, onClose, title }: ModalProps) {
  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/30 p-4 backdrop-blur-sm">
      <div className="w-full max-w-lg rounded-[28px] bg-sand p-5 shadow-panel">
        <div className="flex items-center justify-between gap-4">
          <h2 className="font-display text-2xl">{title}</h2>
          <button className="text-sm text-ink/65" onClick={onClose} type="button">
            Close
          </button>
        </div>
        <div className="mt-4">{children}</div>
      </div>
    </div>
  );
}

