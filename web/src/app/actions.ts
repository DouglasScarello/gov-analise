"use server";

import { cookies } from "next/headers";

export type Tema = "claro" | "escuro";

const COOKIE_TEMA = "tema";

export async function definirTema(tema: Tema) {
  const cookieStore = await cookies();
  cookieStore.set(COOKIE_TEMA, tema, {
    maxAge: 60 * 60 * 24 * 365,
    path: "/",
    sameSite: "lax",
  });
}
