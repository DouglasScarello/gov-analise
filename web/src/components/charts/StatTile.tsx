"use client";

type Ponto = { data: string; valor: number };

interface StatTileProps {
  titulo: string;
  valor?: number;
  unidade?: string;
  pontos?: Ponto[];
  semântica?: "neutro" | "melhor_queda" | "melhor_alta";
}

function detectarFrequencia(pontos: Ponto[]): "diaria" | "mensal" | "anual" {
  if (!pontos || pontos.length < 2) return "mensal";

  // Pontos em ordem crescente, pegar os últimos dois para medir frequência recente
  const idx1 = pontos.length - 2;
  const idx2 = pontos.length - 1;
  const data1 = new Date(pontos[idx1].data);
  const data2 = new Date(pontos[idx2].data);
  const diasDiferenca = Math.abs((data2.getTime() - data1.getTime()) / (1000 * 60 * 60 * 24));

  if (diasDiferenca <= 1.5) return "diaria";
  if (diasDiferenca >= 25 && diasDiferenca <= 35) return "mensal";
  return "anual";
}

function calcularVariacao(
  pontos: Ponto[],
  tipo: "mom" | "yoy",
  frequencia: "diaria" | "mensal" | "anual"
): { valor: number; sinal: "sobe" | "desce" | "estável" } | null {
  if (!pontos || pontos.length < 2) return null;

  let intervalo = 0;

  if (tipo === "mom") {
    if (frequencia === "diaria") intervalo = 21; // ~1 mês de dias úteis
    else if (frequencia === "mensal") intervalo = 1;
    else if (frequencia === "anual") return null; // MoM não faz sentido para anual
  } else {
    // YoY
    if (frequencia === "diaria") intervalo = 252; // ~1 ano de dias úteis
    else if (frequencia === "mensal") intervalo = 12;
    else if (frequencia === "anual") intervalo = 1;
  }

  if (intervalo === 0 || pontos.length < intervalo + 1) return null;

  // Pontos vêm em ordem crescente (mais antigos primeiro)
  const ultimoIdx = pontos.length - 1;
  const recente = pontos[ultimoIdx]?.valor;
  const anterior = pontos[ultimoIdx - intervalo]?.valor;

  if (recente === undefined || anterior === undefined) return null;
  if (anterior === 0) return null;

  const pct = ((recente - anterior) / Math.abs(anterior)) * 100;
  return {
    valor: Math.abs(pct),
    sinal: pct > 0.01 ? "sobe" : pct < -0.01 ? "desce" : "estável",
  };
}

function corDaVariacao(
  sinal: "sobe" | "desce" | "estável",
  semântica: "neutro" | "melhor_queda" | "melhor_alta"
): string {
  if (sinal === "estável") return "text-neutral-500";
  if (semântica === "melhor_queda") return sinal === "desce" ? "text-green-600" : "text-red-600";
  if (semântica === "melhor_alta") return sinal === "sobe" ? "text-green-600" : "text-red-600";
  return "text-neutral-500";
}

export default function StatTile({
  titulo,
  valor,
  unidade = "",
  pontos = [],
  semântica = "neutro",
}: StatTileProps) {
  const frequencia = detectarFrequencia(pontos);
  const mom = calcularVariacao(pontos, "mom", frequencia);
  const yoy = calcularVariacao(pontos, "yoy", frequencia);

  // Pontos vêm em ordem crescente (mais antigos primeiro), pegar o último
  const exibirValor = valor ?? pontos[pontos.length - 1]?.valor;

  return (
    <div className="rounded-xl border border-neutral-200 p-4 dark:border-neutral-800">
      <p className="text-xs font-medium text-neutral-500 dark:text-neutral-400">{titulo}</p>
      <div className="mt-2">
        {exibirValor !== undefined ? (
          <>
            <p className="text-2xl font-bold">
              {exibirValor.toLocaleString("pt-BR", {
                maximumFractionDigits: exibirValor > 100 ? 0 : 2,
              })}
              <span className="text-sm text-neutral-500">{unidade}</span>
            </p>
            <div className="mt-1 flex gap-3 text-xs">
              {mom && (
                <span className={`flex items-center gap-1 ${corDaVariacao(mom.sinal, semântica)}`}>
                  <span>{mom.sinal === "sobe" ? "▲" : "▼"}</span>
                  <span>{mom.valor.toFixed(1)}% MoM</span>
                </span>
              )}
              {yoy && (
                <span className={`flex items-center gap-1 ${corDaVariacao(yoy.sinal, semântica)}`}>
                  <span>{yoy.sinal === "sobe" ? "▲" : "▼"}</span>
                  <span>{yoy.valor.toFixed(1)}% YoY</span>
                </span>
              )}
            </div>
          </>
        ) : (
          <p className="py-4 text-center text-sm text-neutral-500">Sem dados disponíveis.</p>
        )}
      </div>
    </div>
  );
}
