import Image from "next/image";
import Link from "next/link";
import type { Pessoa } from "@/lib/api";

export default function PoliticoCard({ pessoa }: { pessoa: Pessoa }) {
  const foto = pessoa.camaraFoto ?? pessoa.senadoFoto;
  const partido = pessoa.camaraPartido ?? pessoa.senadoPartido;
  const uf = pessoa.camaraUf ?? pessoa.senadoUf;

  return (
    <Link
      href={`/politico/${pessoa.slug}`}
      className="flex items-center gap-4 rounded-2xl border border-neutral-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-400 hover:shadow-md dark:border-neutral-800 dark:bg-neutral-900"
    >
      {foto ? (
        <Image
          src={foto}
          alt={pessoa.nome}
          width={64}
          height={64}
          unoptimized
          className="h-16 w-16 shrink-0 rounded-full object-cover ring-2 ring-neutral-100 dark:ring-neutral-800"
        />
      ) : (
        <div className="h-16 w-16 shrink-0 rounded-full bg-neutral-200 dark:bg-neutral-800" />
      )}
      <div className="min-w-0">
        <p className="truncate font-medium text-neutral-900 dark:text-neutral-100">
          {pessoa.nome}
        </p>
        <div className="mt-1 flex flex-wrap items-center gap-2">
          {partido && (
            <span className="rounded-full bg-blue-50 px-2 py-0.5 text-xs font-semibold text-blue-700 dark:bg-blue-950 dark:text-blue-300">
              {partido}
            </span>
          )}
          <span className="text-xs text-neutral-500">{uf}</span>
          <span className="text-xs text-neutral-400">· {pessoa.casa}</span>
        </div>
      </div>
    </Link>
  );
}
