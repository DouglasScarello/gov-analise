import Image from "next/image";
import { notFound } from "next/navigation";
import { obterPessoa } from "@/lib/api";

function formatarData(iso: string | null) {
  if (!iso) return null;
  return new Date(iso).toLocaleDateString("pt-BR");
}

export default async function PoliticoPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;

  let pessoa;
  try {
    pessoa = await obterPessoa(slug);
  } catch {
    notFound();
  }

  const foto = pessoa.camaraFoto ?? pessoa.senadoFoto;
  const partido = pessoa.camaraPartido ?? pessoa.senadoPartido;
  const uf = pessoa.camaraUf ?? pessoa.senadoUf;

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <div className="flex items-center gap-4">
        {foto ? (
          <Image
            src={foto}
            alt={pessoa.nome}
            width={88}
            height={88}
            className="h-22 w-22 rounded-full object-cover ring-2 ring-neutral-200 dark:ring-neutral-800"
            unoptimized
          />
        ) : (
          <div className="h-22 w-22 shrink-0 rounded-full bg-neutral-200 dark:bg-neutral-800" />
        )}
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{pessoa.nome}</h1>
          <p className="text-neutral-500">
            {partido} · {uf} · {pessoa.casa}
          </p>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-2">
        {pessoa.camaraId && (
          <span className="rounded-full bg-blue-50 px-3 py-1 text-sm text-blue-700 dark:bg-blue-950 dark:text-blue-300">
            Deputado(a) federal
          </span>
        )}
        {pessoa.senadoId && (
          <span className="rounded-full bg-emerald-50 px-3 py-1 text-sm text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
            Senador(a)
          </span>
        )}
      </div>

      <section className="mt-8">
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
          Sanções vinculadas ao nome
        </h2>
        {pessoa.sancoesVinculadas.length === 0 ? (
          <p className="text-sm text-neutral-500">Nenhuma sanção encontrada com esse nome.</p>
        ) : (
          <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
            {pessoa.sancoesVinculadas.map((s) => (
              <li key={s.id} className="px-4 py-3">
                <p className="font-medium">{s.sancionadoNome}</p>
                <p className="text-sm text-neutral-500">
                  {s.tipoSancao} · {s.origemSancao} · {formatarData(s.dataInicioSancao)}
                </p>
              </li>
            ))}
          </ul>
        )}
        <p className="mt-2 text-xs text-neutral-400">
          Cruzamento por nome — pode incluir homônimos, já que não há um identificador único
          público entre as fontes.
        </p>
      </section>

      {pessoa.senadoId && (
        <section className="mt-8">
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
            Votações recentes no Senado
          </h2>
          {pessoa.votacoesRecentes.length === 0 ? (
            <p className="text-sm text-neutral-500">Nenhuma votação recente encontrada.</p>
          ) : (
            <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
              {pessoa.votacoesRecentes.map((v, i) => (
                <li key={i} className="px-4 py-3">
                  <p className="font-medium">
                    {v.materiaSigla} {v.materiaNumero}/{v.materiaAno}
                  </p>
                  <p className="text-sm text-neutral-500">
                    Voto: {v.voto} · Resultado: {v.descricaoResultado} · {formatarData(v.dataSessao)}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </div>
  );
}
