"use client";

import { useState } from "react";

import { Card } from "@/components/ui/Card";
import type { ParseResponse, PTTItem } from "@/lib/api";
import type { components } from "@/types/api";

type Metadata = components["schemas"]["DocumentMetadata"];
type BancaMember = components["schemas"]["BancaMember"];

const ABAS = [
  { id: "gerais", label: "Dados gerais" },
  { id: "banca", label: "Orientação e banca" },
  { id: "ptts", label: "Produtos técnicos" },
  { id: "siglas", label: "Abreviaturas e siglas" },
] as const;

type Aba = (typeof ABAS)[number]["id"];

const campo =
  "mt-1 w-full rounded-md border border-[#d9d1c3] bg-white px-3 py-2 text-sm outline-none focus:border-[#0f3d32]";

export function Step3MetadataReview({
  data,
  subtitulo,
  onSubtitulo,
  onChange,
  onBack,
  onNext,
}: {
  data: ParseResponse;
  subtitulo: string;
  onSubtitulo: (value: string) => void;
  onChange: (next: ParseResponse) => void;
  onBack: () => void;
  onNext: () => void;
}) {
  const [aba, setAba] = useState<Aba>("gerais");

  function patchMetadata(partial: Partial<Metadata>) {
    onChange({ ...data, metadata: { ...data.metadata, ...partial } });
  }

  function patchBanca(index: number, partial: Partial<BancaMember>) {
    const banca = data.banca.map((membro, i) => (i === index ? { ...membro, ...partial } : membro));
    onChange({ ...data, banca });
  }

  function patchPtt(index: number, partial: Partial<PTTItem>) {
    const ptts = data.ptts.map((item, i) => (i === index ? { ...item, ...partial } : item));
    onChange({ ...data, ptts });
  }

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-wrap gap-2" role="tablist">
        {ABAS.map((item) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-selected={aba === item.id}
            onClick={() => setAba(item.id)}
            className={`rounded-full px-3 py-1.5 text-sm ${
              aba === item.id ? "bg-[#0f3d32] text-white" : "bg-white text-[#4a453c] ring-1 ring-[#e4dccf]"
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      {aba === "gerais" && (
        <Card title="Dados gerais">
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="text-sm sm:col-span-2">
              Título
              <input
                className={campo}
                value={data.metadata.titulo}
                onChange={(event) => patchMetadata({ titulo: event.target.value })}
              />
            </label>
            <label className="text-sm sm:col-span-2">
              Subtítulo
              <input className={campo} value={subtitulo} onChange={(event) => onSubtitulo(event.target.value)} />
            </label>
            <label className="text-sm">
              Autor
              <input
                className={campo}
                value={data.metadata.autor}
                onChange={(event) => patchMetadata({ autor: event.target.value })}
              />
            </label>
            <label className="text-sm">
              Local
              <input
                className={campo}
                value={data.metadata.local}
                onChange={(event) => patchMetadata({ local: event.target.value })}
              />
            </label>
            <label className="text-sm">
              Ano
              <input
                className={campo}
                value={data.metadata.ano}
                onChange={(event) => patchMetadata({ ano: event.target.value })}
              />
            </label>
            <label className="text-sm">
              Área de concentração
              <input
                className={campo}
                value={data.metadata.area_concentracao}
                onChange={(event) => patchMetadata({ area_concentracao: event.target.value })}
              />
            </label>
          </div>
        </Card>
      )}

      {aba === "banca" && (
        <Card title="Orientação e banca">
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="text-sm">
              Orientador(a)
              <input
                className={campo}
                value={data.metadata.orientador}
                onChange={(event) => patchMetadata({ orientador: event.target.value })}
              />
            </label>
            <label className="text-sm">
              Coorientador(a)
              <input
                className={campo}
                value={data.metadata.coorientador}
                onChange={(event) => patchMetadata({ coorientador: event.target.value })}
              />
            </label>
          </div>
          <ul className="mt-4 flex flex-col gap-3">
            {data.banca.map((membro, index) => (
              <li key={index} className="grid gap-2 rounded-lg border border-[#efe8dc] p-3 sm:grid-cols-4">
                <input
                  aria-label="Nome do membro"
                  className="rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                  value={membro.nome}
                  onChange={(event) => patchBanca(index, { nome: event.target.value })}
                />
                <input
                  aria-label="Função"
                  className="rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                  value={membro.funcao}
                  onChange={(event) => patchBanca(index, { funcao: event.target.value })}
                />
                <input
                  aria-label="Instituição"
                  className="rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                  value={membro.instituicao}
                  onChange={(event) => patchBanca(index, { instituicao: event.target.value })}
                />
                <button
                  type="button"
                  className="text-sm text-red-800"
                  onClick={() => onChange({ ...data, banca: data.banca.filter((_, i) => i !== index) })}
                >
                  Remover
                </button>
              </li>
            ))}
          </ul>
          <button
            type="button"
            className="mt-3 text-sm font-medium text-[#0f3d32]"
            onClick={() =>
              onChange({
                ...data,
                banca: [...data.banca, { nome: "", funcao: "Avaliador", instituicao: "", titulacao: "" }],
              })
            }
          >
            Adicionar membro
          </button>
        </Card>
      )}

      {aba === "ptts" && (
        <Card title="Produtos técnicos (PTTs)">
          {data.ptts.length === 0 ? (
            <p className="text-sm text-[#5c564c]">Nenhum produto técnico foi extraído.</p>
          ) : (
            <ul className="flex flex-col gap-3">
              {data.ptts.map((item, index) => (
                <li key={`${item.num}-${index}`} className="grid gap-2 rounded-lg border border-[#efe8dc] p-3 sm:grid-cols-[1fr_9rem]">
                  <div>
                    <p className="text-xs text-[#6b645a]">{item.num || `PTT ${index + 1}`}</p>
                    <input
                      aria-label="Título do produto"
                      className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                      value={item.titulo || item.nome}
                      onChange={(event) => patchPtt(index, { titulo: event.target.value })}
                    />
                  </div>
                  <label className="text-xs text-[#6b645a]">
                    Impacto
                    <select
                      className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                      value={item.impacto}
                      onChange={(event) => patchPtt(index, { impacto: event.target.value })}
                    >
                      {["", "Alto", "Médio", "Baixo", item.impacto]
                        .filter((valor, i, lista) => valor !== undefined && lista.indexOf(valor) === i)
                        .map((valor) => (
                          <option key={valor || "vazio"} value={valor}>
                            {valor || "Não informado"}
                          </option>
                        ))}
                    </select>
                  </label>
                </li>
              ))}
            </ul>
          )}
        </Card>
      )}

      {aba === "siglas" && (
        <Card title="Abreviaturas e siglas">
          <ul className="flex flex-col gap-2">
            {data.siglas.map(([sigla, expansao], index) => (
              <li key={index} className="grid grid-cols-[8rem_1fr_auto] gap-2">
                <input
                  aria-label="Sigla"
                  className="rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                  value={sigla}
                  onChange={(event) => {
                    const siglas = data.siglas.map((par, i) =>
                      i === index ? ([event.target.value, par[1]] as [string, string]) : par,
                    );
                    onChange({ ...data, siglas });
                  }}
                />
                <input
                  aria-label="Expansão"
                  className="rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                  value={expansao}
                  onChange={(event) => {
                    const siglas = data.siglas.map((par, i) =>
                      i === index ? ([par[0], event.target.value] as [string, string]) : par,
                    );
                    onChange({ ...data, siglas });
                  }}
                />
                <button
                  type="button"
                  className="text-sm text-red-800"
                  onClick={() => onChange({ ...data, siglas: data.siglas.filter((_, i) => i !== index) })}
                >
                  Remover
                </button>
              </li>
            ))}
          </ul>
          <button
            type="button"
            className="mt-3 text-sm font-medium text-[#0f3d32]"
            onClick={() => onChange({ ...data, siglas: [...data.siglas, ["", ""]] })}
          >
            Adicionar sigla
          </button>
        </Card>
      )}

      <div className="flex justify-between gap-3">
        <button
          type="button"
          onClick={onBack}
          className="inline-flex h-11 items-center rounded-md border border-[#d9d1c3] bg-white px-4 text-sm font-medium"
        >
          Voltar
        </button>
        <button
          type="button"
          onClick={onNext}
          className="inline-flex h-11 items-center rounded-md bg-[#0f3d32] px-5 text-sm font-medium text-white hover:bg-[#145244]"
        >
          Confirmar e Padronizar
        </button>
      </div>
    </div>
  );
}
