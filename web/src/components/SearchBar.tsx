"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function SearchBar({ valorInicial = "" }: { valorInicial?: string }) {
  const [termo, setTermo] = useState(valorInicial);
  const router = useRouter();

  function buscar(e: React.FormEvent) {
    e.preventDefault();
    const q = termo.trim();
    if (q.length < 2) return;
    router.push(`/busca?q=${encodeURIComponent(q)}`);
  }

  return (
    <form onSubmit={buscar} className="flex w-full gap-2">
      <input
        type="search"
        value={termo}
        onChange={(e) => setTermo(e.target.value)}
        placeholder="Busque um político, empresa ou órgão público..."
        className="min-w-0 flex-1 rounded-full border border-neutral-300 bg-white px-5 py-3 text-base text-neutral-900 shadow-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-100"
      />
      <button
        type="submit"
        className="shrink-0 rounded-full bg-blue-600 px-6 py-3 text-base font-medium text-white transition hover:bg-blue-700 active:bg-blue-800"
      >
        Buscar
      </button>
    </form>
  );
}
