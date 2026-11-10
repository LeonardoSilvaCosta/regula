"use client";

import { Loader2 } from "lucide-react";

import { Card } from "@/components/ui/Card";
import type { AcademicLevel, ParseResponse } from "@/lib/api";
import type { components } from "@/types/api";

const TIPOS: Record<components["schemas"]["DocumentType"], string> = {
  qualificacao: "Relatório de Qualificação",
  dissertacao: "Dissertação de Mestrado",
  tese: "Tese de Doutorado",
  protocolo_cep: "Protocolo CEP",
  projeto_completo_cep: "Projeto Completo CEP",
};

export function Step4Export({
  tipoDocumento,
  nivel,
  data,
  isGenerating,
  error,
  downloaded,
  onGenerate,
  onReset,
  onBack,
}: {
  tipoDocumento: components["schemas"]["DocumentType"];
  nivel: AcademicLevel;
  data: ParseResponse;
  isGenerating: boolean;
  error: string | null;
  downloaded: boolean;
  onGenerate: () => void;
  onReset: () => void;
  onBack: () => void;
}) {
  return (
    <div className="flex flex-col gap-5">
      <Card title="Resumo da padronização">
        <dl className="grid gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-[#6b645a]">Tipo</dt>
            <dd className="font-medium">{TIPOS[tipoDocumento]}</dd>
          </div>
          <div>
            <dt className="text-[#6b645a]">Nível</dt>
            <dd className="font-medium capitalize">{nivel}</dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="text-[#6b645a]">Título</dt>
            <dd className="font-medium">{data.metadata.titulo || "Sem título"}</dd>
          </div>
          <div>
            <dt className="text-[#6b645a]">Autor</dt>
            <dd className="font-medium">{data.metadata.autor || "—"}</dd>
          </div>
          <div>
            <dt className="text-[#6b645a]">Ano</dt>
            <dd className="font-medium">{data.metadata.ano || "—"}</dd>
          </div>
          {tipoDocumento === "projeto_completo_cep" ? (
            <div>
              <dt className="text-[#6b645a]">Orientador(a)</dt>
              <dd className="font-medium">{data.metadata.orientador || "—"}</dd>
            </div>
          ) : (
            <>
              <div>
                <dt className="text-[#6b645a]">Banca</dt>
                <dd className="font-medium">{data.banca.length} membro(s)</dd>
              </div>
              <div>
                <dt className="text-[#6b645a]">PTTs</dt>
                <dd className="font-medium">{data.ptts.length} produto(s)</dd>
              </div>
            </>
          )}
        </dl>
      </Card>

      {error && (
        <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-900" role="alert">
          {error}
        </p>
      )}
      {downloaded && (
        <p className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-950" role="status">
          Download iniciado: Documento_Padronizado_PPGSP.docx
        </p>
      )}

      <div className="flex flex-wrap items-center justify-between gap-3">
        <button
          type="button"
          onClick={onBack}
          className="inline-flex h-11 items-center rounded-md border border-[#d9d1c3] bg-white px-4 text-sm font-medium"
        >
          Voltar
        </button>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={onReset}
            className="inline-flex h-11 items-center rounded-md border border-[#d9d1c3] bg-white px-4 text-sm font-medium"
          >
            Padronizar Outro Documento
          </button>
          <button
            type="button"
            disabled={isGenerating}
            onClick={onGenerate}
            className="inline-flex h-11 items-center gap-2 rounded-md bg-[#0f3d32] px-5 text-sm font-medium text-white hover:bg-[#145244] disabled:opacity-60"
          >
            {isGenerating && <Loader2 className="size-4 animate-spin" aria-hidden />}
            {isGenerating ? "Gerando documento…" : "Gerar Documento Padronizado (.docx)"}
          </button>
        </div>
      </div>
    </div>
  );
}
