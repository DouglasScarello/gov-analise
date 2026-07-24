"use client";

import { useState } from "react";

type Periodo = "1a" | "5a" | "10a" | "tudo";

export function usePeriodo() {
  const [periodo, setPeriodo] = useState<Periodo>("10a");
  return { periodo, setPeriodo };
}

export function PeriodoSelector({ periodo, onChange }: { periodo: Periodo; onChange: (p: Periodo) => void }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Período:</span>
      <div className="flex gap-1">
        {(["1a", "5a", "10a", "tudo"] as const).map((p) => (
          <button
            key={p}
            onClick={() => onChange(p)}
            className={`rounded-lg px-3 py-1 text-xs font-medium transition-colors ${
              periodo === p
                ? "bg-blue-600 text-white"
                : "border border-neutral-300 text-neutral-700 hover:border-blue-500 hover:text-blue-600 dark:border-neutral-700 dark:text-neutral-300"
            }`}
          >
            {p === "1a" ? "1 ano" : p === "5a" ? "5 anos" : p === "10a" ? "10 anos" : "Tudo"}
          </button>
        ))}
      </div>
    </div>
  );
}
