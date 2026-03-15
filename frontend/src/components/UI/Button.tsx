import type { ButtonHTMLAttributes, PropsWithChildren } from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost';

interface ButtonProps extends PropsWithChildren<ButtonHTMLAttributes<HTMLButtonElement>> {
  variant?: ButtonVariant;
}

const variantClassNames: Record<ButtonVariant, string> = {
  primary:
    'bg-ink text-white hover:bg-ink/90 disabled:bg-ink/25 disabled:text-white/70',
  secondary:
    'bg-accent text-white hover:bg-accent/90 disabled:bg-accent/25 disabled:text-white/70',
  ghost:
    'border border-ink/10 bg-white/70 text-ink hover:bg-white disabled:text-ink/30',
};

export function Button({
  children,
  className = '',
  variant = 'primary',
  ...props
}: ButtonProps) {
  return (
    <button
      className={`inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-medium transition ${variantClassNames[variant]} ${className}`.trim()}
      {...props}
    >
      {children}
    </button>
  );
}

