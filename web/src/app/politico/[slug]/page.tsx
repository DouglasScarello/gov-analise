import Image from "next/image";
import { notFound } from "next/navigation";
import { obterPessoa } from "@/lib/api";

function formatarData(iso: string | null) {
  if (!iso) return null;
  return new Date(iso).toLocaleDateString("pt-BR");
}

function formatarMoeda(valor: number | null) {
  if (valor == null) return "valor não informado";
  return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

const VALORES_INVALIDOS = ["#NULO", "#NULO#", "#NE", "#NE#", "NÃO DIVULGÁVEL", "NÃO INFORMADO"];

function campoValido(valor: string | null | undefined): valor is string {
  return !!valor && !VALORES_INVALIDOS.includes(valor.toUpperCase());
}

function titleCase(valor: string) {
  return valor
    .toLowerCase()
    .split(" ")
    .map((p) => (p.length > 2 ? p[0].toUpperCase() + p.slice(1) : p))
    .join(" ");
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

      {(campoValido(pessoa.genero) || campoValido(pessoa.corRaca) || campoValido(pessoa.escolaridade) || campoValido(pessoa.ocupacao)) && (
        <dl className="mt-6 grid grid-cols-2 gap-4 text-sm sm:grid-cols-4">
          {campoValido(pessoa.genero) && (
            <div>
              <dt className="text-neutral-500">Gênero</dt>
              <dd className="font-medium">{titleCase(pessoa.genero)}</dd>
            </div>
          )}
          {campoValido(pessoa.corRaca) && (
            <div>
              <dt className="text-neutral-500">Cor/raça (autodeclarada)</dt>
              <dd className="font-medium">{titleCase(pessoa.corRaca)}</dd>
            </div>
          )}
          {campoValido(pessoa.escolaridade) && (
            <div>
              <dt className="text-neutral-500">Escolaridade</dt>
              <dd className="font-medium">{titleCase(pessoa.escolaridade)}</dd>
            </div>
          )}
          {campoValido(pessoa.ocupacao) && (
            <div>
              <dt className="text-neutral-500">Ocupação declarada</dt>
              <dd className="font-medium">{titleCase(pessoa.ocupacao)}</dd>
            </div>
          )}
        </dl>
      )}

      {pessoa.totalProposicoes > 0 && (
        <section className="mt-8">
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
            Proposições de autoria
          </h2>
          <p className="mb-3 text-sm text-neutral-600 dark:text-neutral-400">
            <span className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100">
              {pessoa.totalProposicoes}
            </span>{" "}
            {pessoa.totalProposicoes === 1 ? "proposição de autoria" : "proposições de autoria"} — projetos
            de lei, propostas de emenda, requerimentos e emendas, como autor principal ou coautor,
            incluindo as de legislaturas anteriores.
          </p>
          <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
            {pessoa.proposicoesRecentes.map((p, i) => (
              <li key={i} className="px-4 py-3">
                <a
                  href={p.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-medium text-blue-600 hover:underline dark:text-blue-400"
                >
                  {p.tipoSigla} {p.numero}/{p.ano}
                </a>
                {p.ementa && (
                  <p className="mt-1 line-clamp-2 text-sm text-neutral-500">{p.ementa}</p>
                )}
                <p className="mt-1 text-xs text-neutral-400">
                  {p.casa === "Camara" ? "Câmara" : "Senado"} · {formatarData(p.dataApresentacao)}
                </p>
              </li>
            ))}
          </ul>
          {pessoa.totalProposicoes > pessoa.proposicoesRecentes.length && (
            <p className="mt-2 text-xs text-neutral-400">
              Mostrando as {pessoa.proposicoesRecentes.length} mais recentes de {pessoa.totalProposicoes}.
            </p>
          )}
        </section>
      )}

      {(pessoa.legislaturasCamara.length > 0 || pessoa.legislaturasSenado.length > 0) && (
        <section className="mt-8">
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
            Histórico de legislaturas
          </h2>
          <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
            {pessoa.legislaturasCamara.map((l) => (
              <li key={`camara-${l.idLegislatura}`} className="px-4 py-3">
                <p className="font-medium">{l.idLegislatura}ª legislatura (Câmara)</p>
                <p className="text-sm text-neutral-500">
                  {l.siglaPartido} · {l.siglaUf}
                </p>
              </li>
            ))}
            {pessoa.legislaturasSenado.map((l) => (
              <li key={`senado-${l.numeroLegislatura}`} className="px-4 py-3">
                <p className="font-medium">{l.numeroLegislatura}ª legislatura (Senado)</p>
                <p className="text-sm text-neutral-500">
                  {l.participacao} · {l.siglaUf} · {formatarData(l.dataInicio)} a {formatarData(l.dataFim)}
                </p>
              </li>
            ))}
          </ul>
        </section>
      )}

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

      <section className="mt-8">
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
          Contratos vinculados ao nome
        </h2>
        {pessoa.contratosVinculados.length === 0 ? (
          <p className="text-sm text-neutral-500">Nenhum contrato encontrado com esse nome.</p>
        ) : (
          <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
            {pessoa.contratosVinculados.map((c, i) => (
              <li key={i} className="px-4 py-3">
                <p className="font-medium">{c.orgaoNome}</p>
                <p className="text-sm text-neutral-500 line-clamp-2">{c.objeto}</p>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">
                  {formatarMoeda(c.valor)} · {formatarData(c.data)}
                </p>
              </li>
            ))}
          </ul>
        )}
        <p className="mt-2 text-xs text-neutral-400">
          Cruzamento por nome do fornecedor — pode incluir homônimos.
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
