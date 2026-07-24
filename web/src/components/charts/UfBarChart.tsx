"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Item = { uf: string; valor: number };

const formatarCompacto = new Intl.NumberFormat("pt-BR", {
  notation: "compact",
  maximumFractionDigits: 1,
}).format;

function CustomTooltip({
  active,
  payload,
  unidade,
}: {
  active?: boolean;
  payload?: { value: number; payload: Item }[];
  unidade?: string;
}) {
  if (!active || !payload?.length) return null;
  const item = payload[0].payload;
  return (
    <div className="rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm shadow-sm dark:border-neutral-700 dark:bg-neutral-900">
      <p className="text-neutral-500 dark:text-neutral-400">{item.uf}</p>
      <p className="font-medium">
        {payload[0].value.toLocaleString("pt-BR", { maximumFractionDigits: 0 })}
        {unidade ?? ""}
      </p>
    </div>
  );
}

export default function UfBarChart({ itens, unidade }: { itens: Item[]; unidade?: string }) {
  if (itens.length === 0) {
    return <p className="py-12 text-center text-sm text-neutral-500">Sem dados disponíveis.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={itens} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
        <CartesianGrid stroke="var(--chart-grid)" vertical={false} />
        <XAxis
          dataKey="uf"
          tick={{ fill: "var(--chart-axis)", fontSize: 12 }}
          axisLine={{ stroke: "var(--chart-grid)" }}
          tickLine={false}
          interval={0}
        />
        <YAxis
          tick={{ fill: "var(--chart-axis)", fontSize: 12 }}
          axisLine={false}
          tickLine={false}
          tickFormatter={formatarCompacto}
          width={48}
        />
        <Tooltip content={<CustomTooltip unidade={unidade} />} cursor={{ fill: "var(--chart-grid)", opacity: 0.4 }} />
        <Bar dataKey="valor" fill="var(--chart-primary)" radius={[4, 4, 0, 0]} maxBarSize={28} />
      </BarChart>
    </ResponsiveContainer>
  );
}
