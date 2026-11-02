import { Check } from "lucide-react";

import { cn } from "@/lib/cn";

const STEPS = [
  { id: 1, label: "Upload" },
  { id: 2, label: "Diagnóstico" },
  { id: 3, label: "Metadados" },
  { id: 4, label: "Exportar" },
] as const;

export function Stepper({ step }: { step: 1 | 2 | 3 | 4 }) {
  return (
    <ol className="grid grid-cols-4 gap-2" aria-label="Progresso do assistente">
      {STEPS.map((item) => {
        const done = item.id < step;
        const current = item.id === step;
        return (
          <li key={item.id} className="min-w-0">
            <div
              className={cn(
                "mb-2 h-1.5 rounded-full",
                done || current ? "bg-[#0f3d32]" : "bg-[#e4dccf]",
              )}
            />
            <p
              className={cn(
                "flex items-center gap-1.5 text-xs font-medium",
                current ? "text-[#0f3d32]" : "text-[#6b645a]",
              )}
              aria-current={current ? "step" : undefined}
            >
              <span
                className={cn(
                  "inline-flex size-5 shrink-0 items-center justify-center rounded-full text-[10px]",
                  done || current ? "bg-[#0f3d32] text-white" : "bg-[#efe8dc] text-[#6b645a]",
                )}
              >
                {done ? <Check className="size-3" aria-hidden /> : item.id}
              </span>
              <span className="truncate">
                Passo {item.id}
                <span className="hidden sm:inline"> · {item.label}</span>
              </span>
            </p>
          </li>
        );
      })}
    </ol>
  );
}
