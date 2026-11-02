import type { ReactNode } from "react";

import { cn } from "@/lib/cn";

const tones = {
  success: "bg-emerald-50 text-emerald-900 ring-emerald-200",
  warning: "bg-amber-50 text-amber-950 ring-amber-200",
  danger: "bg-red-50 text-red-900 ring-red-200",
  neutral: "bg-[#f7f3ea] text-[#4a453c] ring-[#e4dccf]",
} as const;

export function Badge({
  tone = "neutral",
  children,
  className,
}: {
  tone?: keyof typeof tones;
  children: ReactNode;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset",
        tones[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
