"use client";

import { useState } from "react";
import { definirTema, type Tema } from "@/app/actions";

export default function ThemeToggle({ temaInicial }: { temaInicial: Tema }) {
  const [tema, setTema] = useState<Tema>(temaInicial);

  function alternar() {
    const novoTema: Tema = tema === "escuro" ? "claro" : "escuro";
    document.documentElement.classList.toggle("dark", novoTema === "escuro");
    setTema(novoTema);
    void definirTema(novoTema);
  }

  return (
    <button
      onClick={alternar}
      aria-label={tema === "escuro" ? "Mudar para tema claro" : "Mudar para tema escuro"}
      title={tema === "escuro" ? "Mudar para tema claro" : "Mudar para tema escuro"}
      className="rounded-full border border-neutral-300 px-3 py-1.5 text-sm hover:border-blue-500 dark:border-neutral-700"
    >
      {tema === "escuro" ? "☀️" : "🌙"}
    </button>
  );
}
