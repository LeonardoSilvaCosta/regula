"use client";

import { useEffect, useState } from "react";
import { BookOpen, FileCheck2, GraduationCap, ScrollText } from "lucide-react";

import { checkHealth } from "@/lib/api";

type ApiStatus = "checking" | "online" | "offline";

export default function Home() {
  const [status, setStatus] = useState<ApiStatus>("checking");

  useEffect(() => {
    let active = true;
    checkHealth()
      .then((body) => {
        if (active) setStatus(body.status === "ok" ? "online" : "offline");
      })
      .catch(() => {
        if (active) setStatus("offline");
      });
    return () => {
      active = false;
    };
  }, []);

  const statusLabel =
    status === "checking" ? "Verificando API…" : status === "online" ? "Online" : "Offline";

  return (
    <div className="flex flex-1 flex-col bg-[#f4f1ea] text-[#1c1915]">
      <header className="border-b border-[#d9d1c3] bg-[#0f3d32] text-[#f7f3ea]">
        <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-6 py-4">
          <p className="text-xs tracking-[0.22em] uppercase">UFPA · PPGSP</p>
          <p className="text-xs text-[#d7c7a3]">Resoluções 007, 009 e 010</p>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col justify-center px-6 py-16">
        <p className="mb-3 text-sm font-medium tracking-wide text-[#0f3d32] uppercase">
          Programa de Pós-Graduação em Segurança Pública
        </p>
        <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-[#0f3d32] sm:text-5xl">
          Padronizador PPGSP/UFPA
        </h1>
        <p className="mt-4 max-w-2xl text-lg leading-8 text-[#4a453c]">
          Apoio à formatação de Relatório de Qualificação, Dissertação e Tese,
          conforme as resoluções do programa.
        </p>

        <ul className="mt-10 grid gap-4 sm:grid-cols-3">
          <li className="rounded-lg border border-[#e4dccf] bg-white p-4">
            <ScrollText className="mb-3 size-5 text-[#0f3d32]" aria-hidden />
            <p className="font-medium">Qualificação</p>
            <p className="mt-1 text-sm text-[#5c564c]">Relatório de qualificação</p>
          </li>
          <li className="rounded-lg border border-[#e4dccf] bg-white p-4">
            <BookOpen className="mb-3 size-5 text-[#0f3d32]" aria-hidden />
            <p className="font-medium">Dissertação</p>
            <p className="mt-1 text-sm text-[#5c564c]">Mestrado</p>
          </li>
          <li className="rounded-lg border border-[#e4dccf] bg-white p-4">
            <GraduationCap className="mb-3 size-5 text-[#0f3d32]" aria-hidden />
            <p className="font-medium">Tese</p>
            <p className="mt-1 text-sm text-[#5c564c]">Doutorado</p>
          </li>
        </ul>

        <div className="mt-10 flex flex-col items-start gap-4 sm:flex-row sm:items-center">
          <button
            type="button"
            className="inline-flex h-11 items-center rounded-md bg-[#0f3d32] px-5 text-sm font-medium text-white hover:bg-[#145244]"
            title="O assistente de padronização será habilitado na próxima etapa"
          >
            Iniciar Padronização
          </button>
          <div
            className="inline-flex items-center gap-2 rounded-full border border-[#e4dccf] bg-white px-3 py-1.5 text-sm"
            role="status"
          >
            <FileCheck2 className="size-4 text-[#0f3d32]" aria-hidden />
            <span className="text-[#5c564c]">API FastAPI</span>
            <span
              className={
                status === "online"
                  ? "font-medium text-emerald-800"
                  : status === "offline"
                    ? "font-medium text-red-800"
                    : "font-medium text-[#5c564c]"
              }
            >
              {statusLabel}
            </span>
          </div>
        </div>
      </main>
    </div>
  );
}
