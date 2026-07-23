"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Ponto = { data: string; valor: number };

function formatarData(iso: string) {
  const [ano, mes] = iso.split("-");
  return `${mes}/${ano.slice(2)}`;
}

function formatarDataCompleta(iso: string) {
  const [ano, mes, dia] = iso.split("-");
  return `${dia.slice(0, 2)}/${mes}/${ano}`;
}

function CustomTooltip({
  active,
  payload,
  unidade,
}: {
  active?: boolean;
  payload?: { value: number; payload: Ponto }[];
  unidade?: string;
}) {
  if (!active || !payload?.length) return null;
  const ponto = payload[0].payload;
  return (
    <div className="rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm shadow-sm dark:border-neutral-700 dark:bg-neutral-900">
      <p className="text-neutral-500 dark:text-neutral-400">{formatarDataCompleta(ponto.data)}</p>
      <p className="font-medium">
        {payload[0].value.toLocaleString("pt-BR", { maximumFractionDigits: 2 })}
        {unidade ?? ""}
      </p>
    </div>
  );
}

export default function SerieLineChart({ pontos, unidade }: { pontos: Ponto[]; unidade?: string }) {
  if (pontos.length === 0) {
    return <p className="py-12 text-center text-sm text-neutral-500">Sem dados disponíveis.</p>;
  }

  const dados = pontos.map((p) => ({ ...p, dataFmt: formatarData(p.data) }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={dados} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
        <CartesianGrid stroke="var(--chart-grid)" vertical={false} />
        <XAxis
          dataKey="dataFmt"
          tick={{ fill: "var(--chart-axis)", fontSize: 12 }}
          axisLine={{ stroke: "var(--chart-grid)" }}
          tickLine={false}
          minTickGap={32}
        />
        <YAxis
          tick={{ fill: "var(--chart-axis)", fontSize: 12 }}
          axisLine={false}
          tickLine={false}
          width={48}
        />
        <Tooltip content={<CustomTooltip unidade={unidade} />} cursor={{ stroke: "var(--chart-grid)" }} />
        <Line
          type="monotone"
          dataKey="valor"
          stroke="var(--chart-primary)"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
