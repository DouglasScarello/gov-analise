import Link from "next/link";
import { notFound } from "next/navigation";
import { obterProposicao } from "@/lib/api";

type Params = { url?: string };

function formatarData(iso: string | null) {
  if (!iso) return "data não informada";
  const [ano, mes, dia] = iso.split("T")[0].split("-");
  return `${dia}/${mes}/${ano}`;
}

function formatarNumero(numero: string, ano: string) {
  const n = numero.endsWith(".0") ? numero.slice(0, -2) : numero;
  const a = ano.endsWith(".0") ? ano.slice(0, -2) : ano;
  return `${n}/${a}`;
}

const EXPLICACAO_TIPO: Record<string, string> = {
  PL: "Projeto de Lei — propõe criar, alterar ou revogar uma lei ordinária.",
  PLP: "Projeto de Lei Complementar — propõe uma lei complementar, usada para temas que a Constituição exige regras mais rígidas de aprovação.",
  PEC: "Proposta de Emenda à Constituição — propõe alterar o texto da própria Constituição Federal; exige aprovação por 3/5 dos votos, em dois turnos, em cada Casa.",
  MPV: "Medida Provisória — norma editada pelo Presidente da República, com força de lei imediata, que precisa ser votada pelo Congresso em até 120 dias ou perde a validade.",
  REQ: "Requerimento — pedido formal de um parlamentar, como convocar uma audiência, pedir informações ou solicitar urgência na tramitação de outra proposta.",
  RQS: "Requerimento (Senado) — pedido formal de um senador, como convocar uma audiência ou solicitar informações.",
  EMC: "Emenda — proposta de alteração ao texto de outra proposição que já está em tramitação.",
  EMP: "Emenda de Plenário — alteração proposta ao texto de uma matéria já em discussão no plenário.",
  RIC: "Requerimento de Informação — pede formalmente que um órgão do governo preste esclarecimentos por escrito.",
  INC: "Indicação — sugestão de um parlamentar para que o Poder Executivo tome determinada providência.",
  DOC: "Documento administrativo interno da Casa legislativa.",
  RPD: "Redação Final — texto consolidado de uma proposição após todas as emendas aprovadas, pronto para votação final ou envio à outra Casa.",
  PDL: "Projeto de Decreto Legislativo — trata de assuntos de competência exclusiva do Congresso, como aprovar tratados internacionais.",
  REC: "Recurso — contesta uma decisão tomada durante a tramitação de uma proposição.",
  SBT: "Substitutivo — texto alternativo que substitui integralmente a proposta original.",
  PRL: "Parecer do Relator — análise e voto do parlamentar responsável por avaliar uma proposição em comissão.",
  MSF: "Mensagem — comunicação oficial do Poder Executivo ao Congresso, como o envio de uma indicação ou veto.",
};

export default async function ProposicaoDetalhePage({
  searchParams,
}: {
  searchParams: Promise<Params>;
}) {
  const sp = await searchParams;
  if (!sp.url) notFound();

  let proposicao;
  try {
    proposicao = await obterProposicao(sp.url);
  } catch {
    notFound();
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <Link href="/proposicoes" className="text-sm text-neutral-500 hover:text-blue-600">
        ← Todas as proposições
      </Link>

      <h1 className="mt-4 text-2xl font-semibold tracking-tight">
        {proposicao.tipoSigla} {formatarNumero(proposicao.numero, proposicao.ano)}
      </h1>
      <p className="mt-1 text-neutral-500">
        {proposicao.casa === "Camara" ? "Câmara dos Deputados" : "Senado Federal"} · apresentada em{" "}
        {formatarData(proposicao.dataApresentacao)}
      </p>

      <div className="mt-6 rounded-xl border border-neutral-200 bg-neutral-50 p-4 text-sm text-neutral-700 dark:border-neutral-800 dark:bg-neutral-900/50 dark:text-neutral-300">
        <p className="font-medium">O que é um(a) {proposicao.tipoSigla}?</p>
        <p className="mt-1">
          {EXPLICACAO_TIPO[proposicao.tipoSigla] ?? "Tipo de proposição legislativa."}
        </p>
      </div>

      {proposicao.ementa && (
        <div className="mt-6">
          <h2 className="mb-1 text-xs font-semibold uppercase tracking-wide text-neutral-500">
            Do que trata
          </h2>
          <p className="text-sm leading-relaxed">{proposicao.ementa}</p>
        </div>
      )}

      <p className="mt-6 text-sm text-neutral-500">
        {proposicao.totalAutores > 1
          ? `Proposta em conjunto por ${proposicao.totalAutores} parlamentares.`
          : "Proposta por 1 parlamentar."}
      </p>

      <a
        href={proposicao.url}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-6 inline-block rounded-full border border-neutral-300 px-4 py-2 text-sm hover:border-blue-500 hover:text-blue-600 dark:border-neutral-700"
      >
        Ver tramitação completa no site oficial ↗
      </a>

      <p className="mt-8 text-xs text-neutral-500 dark:text-neutral-400">
        Esta página resume os dados públicos da proposição. Para o texto integral, pareceres e o
        histórico completo de tramitação, consulte o site oficial da{" "}
        {proposicao.casa === "Camara" ? "Câmara dos Deputados" : "Senado Federal"} acima.
      </p>
    </div>
  );
}
