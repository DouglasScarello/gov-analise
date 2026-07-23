"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function FiltroNome({
  action,
  valorInicial = "",
  placeholder = "Buscar por nome...",
}: {
  action: string;
  valorInicial?: string;
  placeholder?: string;
}) {
  const [termo, setTermo] = useState(valorInicial);
  const router = useRouter();

  function aplicar(e: React.FormEvent) {
    e.preventDefault();
    const qs = new URLSearchParams(window.location.search);
    const t = termo.trim();
    if (t) {
      qs.set("nome", t);
    } else {
      qs.delete("nome");
    }
    qs.delete("pagina");
    router.push(`${action}?${qs.toString()}`);
  }

  return (
    <form onSubmit={aplicar} className="flex w-full gap-2">
      <input
        type="search"
        value={termo}
        onChange={(e) => setTermo(e.target.value)}
        placeholder={placeholder}
        className="min-w-0 flex-1 rounded-full border border-neutral-300 bg-white px-4 py-2 text-sm text-neutral-900 shadow-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-100"
      />
      <button
        type="submit"
        className="shrink-0 rounded-full bg-blue-600 px-5 py-2 text-sm font-medium text-white transition hover:bg-blue-700 active:bg-blue-800"
      >
        Buscar
      </button>
    </form>
  );
}
