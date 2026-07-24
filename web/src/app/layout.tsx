import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { cookies } from "next/headers";
import Link from "next/link";
import ThemeToggle from "@/components/ThemeToggle";
import type { Tema } from "./actions";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Gov Analise — Transparência pública em um só lugar",
  description:
    "Busque políticos, empresas e contratos públicos cruzando dados abertos do governo brasileiro.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#1d4ed8",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  const tema: Tema = cookieStore.get("tema")?.value === "escuro" ? "escuro" : "claro";

  return (
    <html
      lang="pt-BR"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased ${tema === "escuro" ? "dark" : ""}`}
    >
      <body className="min-h-full flex flex-col bg-neutral-50 text-neutral-900 dark:bg-neutral-950 dark:text-neutral-100">
        <header className="border-b border-neutral-200 bg-white dark:border-neutral-800 dark:bg-neutral-900">
          <div className="mx-auto flex max-w-4xl items-center justify-between gap-3 px-4 py-3">
            <Link href="/" className="shrink-0 text-lg font-semibold tracking-tight">
              Gov<span className="text-blue-600">Analise</span>
            </Link>
            <div className="flex min-w-0 items-center gap-2">
              <Link
                href="/politicos"
                className="shrink-0 rounded-full border border-neutral-300 px-3 py-2 text-sm hover:border-blue-500 hover:text-blue-600 dark:border-neutral-700"
              >
                Políticos
              </Link>
              <Link
                href="/legislativo"
                className="hidden shrink-0 rounded-full border border-neutral-300 px-3 py-2 text-sm hover:border-blue-500 hover:text-blue-600 dark:border-neutral-700 sm:inline-block"
              >
                Legislativo
              </Link>
              <Link
                href="/proposicoes"
                className="hidden shrink-0 rounded-full border border-neutral-300 px-3 py-2 text-sm hover:border-blue-500 hover:text-blue-600 dark:border-neutral-700 md:inline-block"
              >
                Proposições
              </Link>
              <Link
                href="/estados"
                className="hidden shrink-0 rounded-full border border-neutral-300 px-3 py-2 text-sm hover:border-blue-500 hover:text-blue-600 dark:border-neutral-700 lg:inline-block"
              >
                Estados
              </Link>
              <details className="group relative shrink-0">
                <summary className="flex list-none items-center gap-1 rounded-full border border-neutral-300 px-3 py-2 text-sm hover:border-blue-500 hover:text-blue-600 dark:border-neutral-700 [&::-webkit-details-marker]:hidden">
                  Mais
                  <span className="transition-transform group-open:rotate-180">▾</span>
                </summary>
                <div className="absolute right-0 z-10 mt-2 flex w-44 flex-col gap-1 rounded-xl border border-neutral-200 bg-white p-2 shadow-lg dark:border-neutral-800 dark:bg-neutral-900">
                  <Link
                    href="/legislativo"
                    className="rounded-lg px-3 py-2 text-sm hover:bg-neutral-100 dark:hover:bg-neutral-800 sm:hidden"
                  >
                    Legislativo
                  </Link>
                  <Link
                    href="/proposicoes"
                    className="rounded-lg px-3 py-2 text-sm hover:bg-neutral-100 dark:hover:bg-neutral-800 md:hidden"
                  >
                    Proposições
                  </Link>
                  <Link
                    href="/estados"
                    className="rounded-lg px-3 py-2 text-sm hover:bg-neutral-100 dark:hover:bg-neutral-800 lg:hidden"
                  >
                    Estados
                  </Link>
                  <Link
                    href="/economia"
                    className="rounded-lg px-3 py-2 text-sm hover:bg-neutral-100 dark:hover:bg-neutral-800"
                  >
                    Economia
                  </Link>
                  <Link
                    href="/sancoes"
                    className="rounded-lg px-3 py-2 text-sm hover:bg-neutral-100 dark:hover:bg-neutral-800"
                  >
                    Sanções
                  </Link>
                  <Link
                    href="/contratos"
                    className="rounded-lg px-3 py-2 text-sm hover:bg-neutral-100 dark:hover:bg-neutral-800"
                  >
                    Contratos
                  </Link>
                  <Link
                    href="/orgaos"
                    className="rounded-lg px-3 py-2 text-sm hover:bg-neutral-100 dark:hover:bg-neutral-800"
                  >
                    Órgãos
                  </Link>
                  <Link
                    href="/judicial"
                    className="rounded-lg px-3 py-2 text-sm hover:bg-neutral-100 dark:hover:bg-neutral-800"
                  >
                    Judiciário
                  </Link>
                  <Link
                    href="/sobre"
                    className="rounded-lg px-3 py-2 text-sm hover:bg-neutral-100 dark:hover:bg-neutral-800"
                  >
                    Sobre
                  </Link>
                </div>
              </details>
            </div>
            <div className="shrink-0">
              <ThemeToggle temaInicial={tema} />
            </div>
          </div>
        </header>
        <main className="flex-1">{children}</main>
        <footer className="border-t border-neutral-200 px-4 py-6 text-center text-sm text-neutral-500 dark:border-neutral-800">
          Dados públicos oficiais — Câmara, Senado, TSE, Bacen, SICONFI, IBGE, Compras.gov.br,
          CNJ DataJud e Portal da Transparência.
        </footer>
      </body>
    </html>
  );
}
