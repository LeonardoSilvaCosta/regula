"use client";

import { useState, type DragEvent } from "react";
import { FileUp, PenLine } from "lucide-react";

import { Card } from "@/components/ui/Card";
import type { AcademicLevel } from "@/lib/api";
import type { components } from "@/types/api";

type DocumentType = components["schemas"]["DocumentType"];

const TIPOS: { value: DocumentType; label: string; disponivel: boolean }[] = [
  { value: "qualificacao", label: "Relatório de Qualificação", disponivel: true },
  { value: "dissertacao", label: "Dissertação de Mestrado", disponivel: false },
  { value: "tese", label: "Tese de Doutorado", disponivel: false },
  { value: "protocolo_cep", label: "Protocolo CEP", disponivel: true },
  { value: "projeto_completo_cep", label: "Projeto Completo CEP", disponivel: true },
  { value: "codebook", label: "Manual de Codificação (Codebook)", disponivel: true },
];

export function Step1Upload({
  file,
  tipoDocumento,
  nivel,
  isParsing,
  error,
  onFile,
  onTipo,
  onNivel,
  onAnalyze,
  onStartDirect,
}: {
  file: File | null;
  tipoDocumento: DocumentType;
  nivel: AcademicLevel;
  isParsing: boolean;
  error: string | null;
  onFile: (file: File | null) => void;
  onTipo: (tipo: DocumentType) => void;
  onNivel: (nivel: AcademicLevel) => void;
  onAnalyze: () => void;
  onStartDirect: () => void;
}) {
  const [over, setOver] = useState(false);

  function accept(next: File | null) {
    if (!next) {
      onFile(null);
      return;
    }
    if (!next.name.toLowerCase().endsWith(".docx")) {
      onFile(null);
      return;
    }
    onFile(next);
  }

  function onDrop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    setOver(false);
    accept(event.dataTransfer.files?.[0] ?? null);
  }

  return (
    <div className="flex flex-col gap-5">
      <Card title="Tipo e nível">
        <fieldset>
          <legend className="mb-2 text-sm font-medium">Tipo de documento</legend>
          <div className="grid gap-2 sm:grid-cols-3">
            {TIPOS.map((tipo) => (
              <label
                key={tipo.value}
                className={`rounded-lg border px-3 py-3 text-sm ${
                  !tipo.disponivel
                    ? "cursor-not-allowed border-[#e4dccf] bg-[#f7f4ef] text-[#8a8175]"
                    : tipoDocumento === tipo.value
                      ? "cursor-pointer border-[#0f3d32] bg-[#eef6f3] font-medium text-[#0f3d32]"
                      : "cursor-pointer border-[#e4dccf]"
                }`}
              >
                <input
                  type="radio"
                  name="tipoDocumento"
                  className="sr-only"
                  disabled={!tipo.disponivel}
                  checked={tipo.disponivel && tipoDocumento === tipo.value}
                  onChange={() => {
                    if (tipo.disponivel) onTipo(tipo.value);
                  }}
                />
                <span className="block">{tipo.label}</span>
                {!tipo.disponivel && (
                  <span className="mt-1 block text-xs font-normal text-[#8a8175]">Ainda não disponível</span>
                )}
              </label>
            ))}
          </div>
        </fieldset>
        <fieldset className="mt-4">
          <legend className="mb-2 text-sm font-medium">Nível</legend>
          <div className="flex gap-2">
            {(["mestrado", "doutorado"] as const).map((opcao) => (
              <label
                key={opcao}
                className={`cursor-pointer rounded-lg border px-4 py-2 text-sm capitalize ${
                  nivel === opcao
                    ? "border-[#0f3d32] bg-[#eef6f3] font-medium text-[#0f3d32]"
                    : "border-[#e4dccf]"
                }`}
              >
                <input
                  type="radio"
                  name="nivel"
                  className="sr-only"
                  checked={nivel === opcao}
                  onChange={() => onNivel(opcao)}
                />
                {opcao}
              </label>
            ))}
          </div>
        </fieldset>
      </Card>

      <div className="grid gap-5 lg:grid-cols-2">
      <Card
        title="Importar de arquivo .docx"
        description="Envie o arquivo .docx que será diagnosticado e padronizado."
      >
        <label
          onDragOver={(event) => {
            event.preventDefault();
            setOver(true);
          }}
          onDragLeave={() => setOver(false)}
          onDrop={onDrop}
          className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed px-6 py-10 text-center ${
            over ? "border-[#0f3d32] bg-[#eef6f3]" : "border-[#cfc6b6] bg-[#fbf9f4]"
          }`}
        >
          <FileUp className="mb-3 size-7 text-[#0f3d32]" aria-hidden />
          <span className="text-sm font-medium text-[#1c1915]">
            Arraste o .docx ou clique para escolher
          </span>
          <span className="mt-1 text-xs text-[#6b645a]">Somente arquivos Word (.docx)</span>
          <input
            type="file"
            accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            className="sr-only"
            onChange={(event) => accept(event.target.files?.[0] ?? null)}
          />
        </label>
        {file && (
          <p className="mt-3 text-sm text-[#0f3d32]">
            Arquivo selecionado: <span className="font-medium">{file.name}</span>
          </p>
        )}
        <div className="mt-4 flex justify-end">
          <button
            type="button"
            disabled={!file || isParsing}
            onClick={onAnalyze}
            className="inline-flex h-11 items-center rounded-md bg-[#0f3d32] px-5 text-sm font-medium text-white hover:bg-[#145244] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isParsing ? "Analisando…" : "Analisar Documento"}
          </button>
        </div>
      </Card>

      <Card
        title="Preencher seções diretamente"
        description="Comece do zero com os textos institucionais do PPGSP, sem importar um .docx."
      >
        <div className="flex h-full flex-col items-start justify-between gap-4 rounded-lg border border-[#0f3d32]/20 bg-[#eef6f3] px-5 py-8">
          <div>
            <PenLine className="mb-3 size-7 text-[#0f3d32]" aria-hidden />
            <p className="text-sm text-[#1c1915]">
              Metadados, banca, siglas e seções normativas ficam em branco para você preencher na revisão.
            </p>
          </div>
          <button
            type="button"
            onClick={onStartDirect}
            className="inline-flex h-11 items-center rounded-md bg-[#0f3d32] px-5 text-sm font-semibold text-white shadow-sm hover:bg-[#145244]"
          >
            Iniciar preenchimento direto
          </button>
        </div>
      </Card>
      </div>

      {error && (
        <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-900" role="alert">
          {error}
        </p>
      )}

    </div>
  );
}
