"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function FiltroContratos({
  orgaoInicial = "",
  fornecedorInicial = "",
}: {
  orgaoInicial?: string;
  fornecedorInicial?: string;
}) {
  const [orgao, setOrgao] = useState(orgaoInicial);
  const [fornecedor, setFornecedor] = useState(fornecedorInicial);
  const router = useRouter();

  function aplicar(e: React.FormEvent) {
    e.preventDefault();
    const qs = new URLSearchParams(window.location.search);
    const setOuRemove = (chave: string, valor: string) => {
      const v = valor.trim();
      if (v) qs.set(chave, v);
      else qs.delete(chave);
    };
    setOuRemove("orgao", orgao);
    setOuRemove("fornecedor", fornecedor);
    qs.delete("pagina");
    router.push(`/contratos?${qs.toString()}`);
  }

  return (
    <form onSubmit={aplicar} className="flex flex-wrap gap-2">
      <input
        type="search"
        value={orgao}
        onChange={(e) => setOrgao(e.target.value)}
        placeholder="Buscar por órgão..."
        className="min-w-0 flex-1 rounded-full border border-neutral-300 bg-white px-4 py-2 text-sm text-neutral-900 shadow-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-100"
      />
      <input
        type="search"
        value={fornecedor}
        onChange={(e) => setFornecedor(e.target.value)}
        placeholder="Buscar por fornecedor..."
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
