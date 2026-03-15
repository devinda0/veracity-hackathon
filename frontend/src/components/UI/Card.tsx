import type { HTMLAttributes, PropsWithChildren } from 'react';

type CardProps = PropsWithChildren<HTMLAttributes<HTMLDivElement>>;

export function Card({ children, className = '', ...props }: CardProps) {
  return (
    <div className={`panel-surface p-5 ${className}`.trim()} {...props}>
      {children}
    </div>
  );
}
