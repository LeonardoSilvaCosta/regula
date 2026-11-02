import type { ReactNode } from "react";

import { cn } from "@/lib/cn";

export function Card({
  title,
  description,
  action,
  children,
  className,
}: {
  title?: string;
  description?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={cn("rounded-xl border border-[#e4dccf] bg-white p-5", className)}>
      {(title || action) && (
        <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
          <div>
            {title && <h2 className="text-base font-semibold text-[#0f3d32]">{title}</h2>}
            {description && <p className="mt-1 text-sm text-[#5c564c]">{description}</p>}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}
