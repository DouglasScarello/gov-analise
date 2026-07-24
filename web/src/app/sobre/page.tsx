export const metadata = {
  title: "Sobre — Gov Analise",
  description: "Metodologia, fontes de dados e limitações conhecidas do Gov Analise.",
};

const FONTES = [
  { nome: "Câmara dos Deputados", url: "https://dadosabertos.camara.leg.br", cobre: "Deputados federais, mandatos por legislatura (1999-2027)" },
  { nome: "Senado Federal", url: "https://legis.senado.leg.br/dadosabertos", cobre: "Senadores, votações nominais, mandatos por legislatura" },
  { nome: "TSE", url: "https://dadosabertos.tse.jus.br", cobre: "Candidatos e eleitos em eleições gerais (1994-2022) e municipais (1996-2024)" },
  { nome: "Banco Central (SGS)", url: "https://www3.bcb.gov.br/sgspub", cobre: "Séries econômicas: Selic, IPCA, IGP-M, dólar, desemprego, dívida pública" },
  { nome: "IBGE (SIDRA)", url: "https://sidra.ibge.gov.br", cobre: "PIB e população por UF, série histórica" },
  { nome: "SICONFI", url: "https://siconfi.tesouro.gov.br", cobre: "Balanços patrimoniais de entes federativos" },
  { nome: "Portal da Transparência (CGU)", url: "https://portaldatransparencia.gov.br/api-de-dados", cobre: "Sanções (CEIS/CNEP) e contratos públicos" },
  { nome: "Compras.gov.br", url: "https://compras.dados.gov.br", cobre: "Contratações públicas federais" },
  { nome: "CNJ DataJud", url: "https://datajud-wiki.cnj.jus.br", cobre: "Amostra recente de processos judiciais em 19 tribunais" },
];

const LIMITACOES = [
  {
    titulo: "Vice-presidente e vice-governador eleitos antes de 2014 não aparecem",
    texto:
      "O arquivo de candidatos do TSE não preenche a situação de eleição desses cargos nas eleições de 1994 a 2010 — todos os candidatos a vice aparecem com o mesmo status \"nulo\", vencedores e perdedores igual. Testamos ligar o vice à chapa do titular eleito pelo número de urna e coligação, e o padrão só se confirmou em ~38% dos casos — insuficiente para publicar sem risco de atribuir o cargo à pessoa errada. Por isso preferimos deixar esses vices de fora das listagens de eleitos, em vez de adivinhar.",
  },
  {
    titulo: "Vice-prefeito eleito antes de 2012 tem a mesma lacuna",
    texto:
      "Nas eleições municipais de 1996 a 2008 a situação de eleição do vice-prefeito também não é registrada pelo TSE. A partir de 2012 isso passou a ser registrado normalmente. Prefeito e vereador não têm essa lacuna em nenhum ano coletado.",
  },
  {
    titulo: "Eleição de 2006 para presidente/vice-presidente não tem resultado na fonte",
    texto: "Só nesse ano específico, o TSE não registrou a situação de eleição para presidente e vice-presidente (governadores de 2006 não têm esse problema).",
  },
  {
    titulo: "Só há foto para políticos de nível federal",
    texto: "Deputados e senadores têm foto via API da Câmara/Senado. Presidente, governadores, deputados estaduais/distritais, prefeitos e vereadores vêm do registro de candidatura do TSE, que não inclui foto.",
  },
  {
    titulo: "Câmara/Senado mostram mandato atual; TSE mostra histórico de candidaturas",
    texto: "O histórico de legislaturas (Câmara e Senado) cobre 1999-2027. Já o TSE cobre candidaturas de todas as eleições gerais e municipais coletadas, não o exercício efetivo do mandato.",
  },
  {
    titulo: "Cruzamento de sanções e contratos é por nome, não por CPF/CNPJ",
    texto: "O CPF nas bases públicas do TSE vem mascarado, então não há identificador único entre as fontes. O cruzamento por nome normalizado pode incluir homônimos — cada seção que faz esse cruzamento avisa isso explicitamente.",
  },
  {
    titulo: "Judiciário (DataJud) é uma amostra recente, não o acervo completo",
    texto: "O DataJud cobre dezenas de milhões de processos por tribunal. Coletamos uma amostra dos processos mais recentemente atualizados em 19 tribunais representativos (5 regiões federais, justiça do trabalho, TSE e os maiores tribunais estaduais), não a base inteira.",
  },
];

export default function SobrePage() {
  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <h1 className="text-2xl font-semibold tracking-tight">Sobre o Gov Analise</h1>
      <p className="mt-2 text-neutral-600 dark:text-neutral-400">
        O Gov Analise cruza dados públicos oficiais do governo brasileiro — políticos, sanções,
        contratos, economia, finanças de entes federativos, legislativo e judiciário — em um único
        lugar de consulta. Não há coleta de dado privado: tudo aqui vem de APIs e portais de dados
        abertos oficiais.
      </p>

      <section className="mt-8">
        <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-neutral-500">
          Fontes de dados
        </h2>
        <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
          {FONTES.map((f) => (
            <li key={f.nome} className="px-4 py-3">
              <p className="font-medium">{f.nome}</p>
              <p className="text-sm text-neutral-500">{f.cobre}</p>
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-8">
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
          Metodologia de cruzamento
        </h2>
        <p className="text-sm text-neutral-600 dark:text-neutral-400">
          Políticos federais (deputados e senadores) são identificados pelo ID numérico oficial da
          Câmara/Senado. Para os demais níveis (estadual e municipal) e para cruzar sanções e
          contratos contra qualquer político, usamos o nome normalizado (maiúsculas, sem acento,
          espaços colapsados) — a fonte pública não disponibiliza um identificador único (CPF) em
          comum entre TSE, Câmara, Senado, CEIS/CNEP e contratos. Esse cruzamento por nome pode,
          eventualmente, incluir homônimos.
        </p>
      </section>

      <section className="mt-8">
        <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-neutral-500">
          Limitações conhecidas
        </h2>
        <ul className="space-y-4">
          {LIMITACOES.map((l) => (
            <li key={l.titulo} className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 dark:border-amber-900 dark:bg-amber-950">
              <p className="font-medium text-amber-900 dark:text-amber-200">{l.titulo}</p>
              <p className="mt-1 text-sm text-amber-800 dark:text-amber-300">{l.texto}</p>
            </li>
          ))}
        </ul>
      </section>

      <p className="mt-8 text-xs text-neutral-500 dark:text-neutral-400">
        Projeto de uso educacional e de pesquisa, distribuído sob licença MIT.
      </p>
    </div>
  );
}
