import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
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

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="pt-BR"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-neutral-50 text-neutral-900 dark:bg-neutral-950 dark:text-neutral-100">
        <header className="border-b border-neutral-200 bg-white dark:border-neutral-800 dark:bg-neutral-900">
          <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
            <Link href="/" className="text-lg font-semibold tracking-tight">
              Gov<span className="text-blue-600">Analise</span>
            </Link>
            <Link
              href="/politicos"
              className="rounded-full border border-neutral-300 px-3 py-1.5 text-sm hover:border-blue-500 hover:text-blue-600 dark:border-neutral-700"
            >
              Políticos
            </Link>
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
