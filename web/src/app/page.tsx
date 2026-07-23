import SearchBar from "@/components/SearchBar";

export default function HomePage() {
  return (
    <div className="mx-auto flex max-w-2xl flex-col items-center gap-8 px-4 py-20 text-center">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
          Transparência pública, em uma busca só
        </h1>
        <p className="mt-3 text-neutral-600 dark:text-neutral-400">
          Cruzamos dados oficiais da Câmara, Senado, TSE, Portal da Transparência e mais
          6 fontes do governo — sem juridiquês, sem planilha.
        </p>
      </div>

      <SearchBar />

      <div className="flex flex-wrap justify-center gap-2 text-sm text-neutral-500">
        <span>Experimente:</span>
        {["Saúde", "Educação", "Petrobras"].map((termo) => (
          <a
            key={termo}
            href={`/busca?q=${encodeURIComponent(termo)}`}
            className="rounded-full border border-neutral-300 px-3 py-1 hover:border-blue-500 hover:text-blue-600 dark:border-neutral-700"
          >
            {termo}
          </a>
        ))}
      </div>
    </div>
  );
}
