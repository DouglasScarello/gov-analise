"use client";

type Ponto = { data: string; valor: number };

interface StatTileProps {
  titulo: string;
  valor?: number;
  unidade?: string;
  pontos?: Ponto[];
  semântica?: "neutro" | "melhor_queda" | "melhor_alta";
}

function calcularVariacao(
  pontos: Ponto[],
  intervalo: number
): { valor: number; sinal: "sobe" | "desce" | "estável" } | null {
  if (!pontos || pontos.length < intervalo + 1) return null;

  const recente = pontos[0]?.valor;
  const anterior = pontos[intervalo]?.valor;

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
  const mom = calcularVariacao(pontos, 1);
  const yoy = calcularVariacao(pontos, 12);

  const exibirValor = valor ?? pontos[0]?.valor;

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
