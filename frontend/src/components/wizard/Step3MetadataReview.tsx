"use client";

import { useState } from "react";

import { Card } from "@/components/ui/Card";
import type { ParseResponse, PTTItem } from "@/lib/api";
import { faixaImpacto } from "@/lib/ptt";
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

const TITULO_PLACEHOLDER = "ESTEIRA PREDITIVA MULTIMODAL DE SUPORTE À DECISÃO CLÍNICA NO CIAP/PMPA";
const SUBTITULO_PLACEHOLDER =
  "Modelos de aprendizado de máquina para predição de desfechos relacionados à saúde mental de policiais militares do Pará a partir de prontuários psicossociais";
const AUTOR_PLACEHOLDER = "Leonardo da Silva Costa";
const ANO_PLACEHOLDER = "2026";
const AREA_PLACEHOLDER = "Segurança Pública, Justiça, Conflitos e Cidadania";
const LINHA_PLACEHOLDER = "Políticas, Gestão, Direitos Humanos, Criminalidade e Tecnologia da Informação";
const INSTITUICAO_ORIENTADOR_PLACEHOLDER = "Universidade Federal do Pará";
const COORDENADOR_PLACEHOLDER = "Prof. Dr. Edson Marcos Leal Soares Ramos";
const ORIENTADOR_PLACEHOLDER = "Prof. Dr. Renato Hidaka Torres";
const IMPACTOS = ["Alto", "Médio", "Baixo"] as const;

const PTT_VAZIO: PTTItem = {
  num: "",
  nome: "",
  autoria: "",
  tipo: "",
  subtipo: "",
  titulo: "",
  ano: "",
  coautoria: "",
  projeto: "",
  financiamento: "",
  financiador: "",
  demanda: "",
  impacto: "",
  justificativa_impacto: "",
  inovacao: "",
  justificativa_inovacao: "",
  complexidade: "",
  justificativa_complexidade: "",
  validacao: "",
  divulgacao: "",
  abrangencia: "",
  publico_usuario: "",
};

function impactoSelecionado(impacto: string): "" | (typeof IMPACTOS)[number] {
  const faixa = faixaImpacto(impacto);
  if (faixa === "alto") return "Alto";
  if (faixa === "medio") return "Médio";
  if (faixa === "baixo") return "Baixo";
  return "";
}

function ehAvaliador(funcao: string) {
  const papel = funcao.toLowerCase();
  return papel.includes("avali") || papel.includes("extern") || (papel.includes("intern") && !papel.includes("orient"));
}

function ehOrientador(funcao: string) {
  const papel = funcao.toLowerCase();
  return papel.includes("orient") && !papel.includes("coorient");
}

function ehCoorientador(funcao: string) {
  return funcao.toLowerCase().includes("coorient");
}

function funcaoCanonico(funcao: string) {
  const papel = funcao.toLowerCase();
  if (papel.includes("coorient")) return "Coorientador(a)";
  if (papel.includes("orient")) return "Orientador(a)";
  if (papel.includes("extern")) return "Avaliador(a) Externo(a)";
  return "Avaliador(a) Interno(a)";
}

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
  const [aviso, setAviso] = useState<string | null>(null);

  function patchMetadata(partial: Partial<Metadata>) {
    onChange({ ...data, metadata: { ...data.metadata, ...partial } });
  }

  function patchBanca(index: number, partial: Partial<BancaMember>) {
    const banca = data.banca.map((membro, i) => (i === index ? { ...membro, ...partial } : membro));
    onChange({ ...data, banca });
  }

  function patchOrientador(nome: string) {
    const banca = data.banca.map((membro) => ({ ...membro }));
    const index = banca.findIndex((membro) => ehOrientador(membro.funcao));
    if (index >= 0) banca[index] = { ...banca[index], nome, funcao: "Orientador(a)" };
    else banca.unshift({ nome, funcao: "Orientador(a)", instituicao: "", titulacao: "" });
    onChange({ ...data, metadata: { ...data.metadata, orientador: nome }, banca });
  }

  function patchCoorientador(nome: string) {
    const banca = data.banca.map((membro) => ({ ...membro }));
    const index = banca.findIndex((membro) => ehCoorientador(membro.funcao));
    if (!nome.trim()) {
      onChange({
        ...data,
        metadata: { ...data.metadata, coorientador: nome },
        banca: index >= 0 ? banca.filter((_, i) => i !== index) : banca,
      });
      return;
    }
    if (index >= 0) {
      banca[index] = { ...banca[index], nome, funcao: "Coorientador(a)" };
    } else {
      const depoisDoOrientador = banca.findIndex((membro) => ehOrientador(membro.funcao));
      const membro: BancaMember = { nome, funcao: "Coorientador(a)", instituicao: "", titulacao: "" };
      if (depoisDoOrientador >= 0) banca.splice(depoisDoOrientador + 1, 0, membro);
      else banca.unshift(membro);
    }
    onChange({ ...data, metadata: { ...data.metadata, coorientador: nome }, banca });
  }

  const indiceOrientador = data.banca.findIndex((membro) => ehOrientador(membro.funcao));
  const indiceCoorientador = data.banca.findIndex((membro) => ehCoorientador(membro.funcao));
  const orientadorBanca = indiceOrientador >= 0 ? data.banca[indiceOrientador] : undefined;
  const coorientadorBanca = indiceCoorientador >= 0 ? data.banca[indiceCoorientador] : undefined;

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
              Título <span className="text-red-800">*</span>
              <input
                required
                className={campo}
                placeholder={TITULO_PLACEHOLDER}
                value={data.metadata.titulo}
                onChange={(event) => patchMetadata({ titulo: event.target.value })}
              />
            </label>
            <label className="text-sm sm:col-span-2">
              Subtítulo
              <input
                className={campo}
                placeholder={SUBTITULO_PLACEHOLDER}
                value={subtitulo}
                onChange={(event) => onSubtitulo(event.target.value)}
              />
            </label>
            <label className="text-sm">
              Autor <span className="text-red-800">*</span>
              <input
                required
                className={campo}
                placeholder={AUTOR_PLACEHOLDER}
                value={data.metadata.autor}
                onChange={(event) => patchMetadata({ autor: event.target.value })}
              />
            </label>
            <label className="text-sm">
              Local <span className="text-red-800">*</span>
              <input
                required
                className={campo}
                value={data.metadata.local}
                onChange={(event) => patchMetadata({ local: event.target.value })}
              />
            </label>
            <label className="text-sm">
              Ano <span className="text-red-800">*</span>
              <input
                required
                className={campo}
                placeholder={ANO_PLACEHOLDER}
                value={data.metadata.ano}
                onChange={(event) => patchMetadata({ ano: event.target.value })}
              />
            </label>
            <label className="text-sm">
              Área de concentração <span className="text-[#6b645a]">(opcional)</span>
              <input
                className={campo}
                placeholder={AREA_PLACEHOLDER}
                value={data.metadata.area_concentracao}
                onChange={(event) => patchMetadata({ area_concentracao: event.target.value })}
              />
            </label>
            <label className="text-sm">
              Linha de pesquisa <span className="text-[#6b645a]">(opcional)</span>
              <input
                className={campo}
                placeholder={LINHA_PLACEHOLDER}
                value={data.metadata.linha_pesquisa}
                onChange={(event) => patchMetadata({ linha_pesquisa: event.target.value })}
              />
            </label>
          </div>
        </Card>
      )}

      {aba === "banca" && (
        <Card title="Coordenação, Orientação e Banca">
          <section>
            <h3 className="text-sm font-semibold tracking-wide text-[#0f3d32]">Coordenação</h3>
            <label className="mt-3 block text-sm">
              Coordenador(a) do programa
              <input
                className={campo}
                placeholder={COORDENADOR_PLACEHOLDER}
                value={data.metadata.coordenador ?? ""}
                onChange={(event) => patchMetadata({ coordenador: event.target.value })}
              />
            </label>
          </section>

          <section className="mt-6 border-t border-[#efe8dc] pt-5">
            <h3 className="text-sm font-semibold tracking-wide text-[#0f3d32]">Orientação</h3>
            <div className="mt-3 grid gap-4 sm:grid-cols-2">
              <label className="text-sm">
                Orientador(a) <span className="text-red-800">*</span>
                <input
                  required
                  className={campo}
                  placeholder={ORIENTADOR_PLACEHOLDER}
                  value={data.metadata.orientador}
                  onChange={(event) => patchOrientador(event.target.value)}
                />
              </label>
              <label className="text-sm">
                Instituição do orientador(a)
                <input
                  className={campo}
                  placeholder={INSTITUICAO_ORIENTADOR_PLACEHOLDER}
                  value={orientadorBanca?.instituicao ?? ""}
                  onChange={(event) => {
                    if (indiceOrientador >= 0) {
                      patchBanca(indiceOrientador, { instituicao: event.target.value });
                      return;
                    }
                    onChange({
                      ...data,
                      banca: [
                        {
                          nome: data.metadata.orientador,
                          funcao: "Orientador(a)",
                          instituicao: event.target.value,
                          titulacao: "",
                        },
                        ...data.banca,
                      ],
                    });
                  }}
                />
              </label>
              <label className="text-sm">
                Coorientador(a) <span className="text-[#6b645a]">(opcional)</span>
                <input
                  className={campo}
                  value={data.metadata.coorientador}
                  onChange={(event) => patchCoorientador(event.target.value)}
                />
              </label>
              {data.metadata.coorientador.trim() ? (
                <label className="text-sm">
                  Instituição do coorientador(a)
                  <input
                    className={campo}
                    placeholder="Instituição"
                    value={coorientadorBanca?.instituicao ?? ""}
                    onChange={(event) => {
                      if (indiceCoorientador >= 0) patchBanca(indiceCoorientador, { instituicao: event.target.value });
                    }}
                  />
                </label>
              ) : null}
            </div>
          </section>

          <section className="mt-6 border-t border-[#efe8dc] pt-5">
            <h3 className="text-sm font-semibold tracking-wide text-[#0f3d32]">Banca</h3>
            <ul className="mt-3 flex flex-col gap-3">
              {data.banca.map((membro, index) => {
                if (index === indiceOrientador || index === indiceCoorientador) return null;
                if (!ehAvaliador(membro.funcao) && !ehAvaliador(funcaoCanonico(membro.funcao))) return null;
                const funcao = funcaoCanonico(membro.funcao);
                return (
                  <li key={index} className="grid gap-2 rounded-lg border border-[#efe8dc] p-3 sm:grid-cols-[1fr_14rem_1fr_auto]">
                    <label className="text-xs text-[#6b645a]">
                      Nome <span className="text-red-800">*</span>
                      <input
                        required
                        aria-label="Nome do avaliador"
                        className="mt-1 w-full rounded-md border border-[#d9d1c3] bg-white px-2 py-1.5 text-sm text-[#1c1915]"
                        value={membro.nome}
                        onChange={(event) => patchBanca(index, { nome: event.target.value })}
                      />
                    </label>
                    <label className="text-xs text-[#6b645a]">
                      Função
                      <select
                        aria-label="Função"
                        className="mt-1 w-full rounded-md border border-[#d9d1c3] bg-white px-2 py-1.5 text-sm"
                        value={funcao}
                        onChange={(event) => patchBanca(index, { funcao: event.target.value })}
                      >
                        <option value="Avaliador(a) Interno(a)">Avaliador(a) Interno(a)</option>
                        <option value="Avaliador(a) Externo(a)">Avaliador(a) Externo(a)</option>
                      </select>
                    </label>
                    <label className="text-xs text-[#6b645a]">
                      Instituição <span className="text-red-800">*</span>
                      <input
                        required
                        aria-label="Instituição do avaliador"
                        className="mt-1 w-full rounded-md border border-[#d9d1c3] bg-white px-2 py-1.5 text-sm"
                        value={membro.instituicao}
                        onChange={(event) => patchBanca(index, { instituicao: event.target.value })}
                      />
                    </label>
                    <button
                      type="button"
                      className="self-end pb-1.5 text-sm text-red-800"
                      onClick={() => onChange({ ...data, banca: data.banca.filter((_, i) => i !== index) })}
                    >
                      Remover
                    </button>
                  </li>
                );
              })}
            </ul>
            <button
              type="button"
              className="mt-3 text-sm font-medium text-[#0f3d32]"
              onClick={() =>
                onChange({
                  ...data,
                  banca: [
                    ...data.banca,
                    { nome: "", funcao: "Avaliador(a) Interno(a)", instituicao: "", titulacao: "" },
                  ],
                })
              }
            >
              Adicionar avaliador
            </button>
          </section>
        </Card>
      )}

      {aba === "ptts" && (
        <Card title="Produtos técnicos (PTTs)">
          {data.ptts.length === 0 ? (
            <p className="text-sm text-[#5c564c]">Nenhum produto técnico foi extraído.</p>
          ) : (
            <ul className="flex flex-col gap-3">
              {data.ptts.map((item, index) => (
                <li key={`${item.num}-${index}`} className="grid gap-2 rounded-lg border border-[#efe8dc] p-3 sm:grid-cols-[1fr_9rem_auto]">
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
                      required
                      className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                      value={impactoSelecionado(item.impacto)}
                      onChange={(event) => patchPtt(index, { impacto: event.target.value })}
                    >
                      <option value="" disabled>
                        Selecione
                      </option>
                      {IMPACTOS.map((valor) => (
                        <option key={valor} value={valor}>
                          {valor}
                        </option>
                      ))}
                    </select>
                  </label>
                  <button
                    type="button"
                    className="self-end pb-1.5 text-sm text-red-800"
                    onClick={() => onChange({ ...data, ptts: data.ptts.filter((_, i) => i !== index) })}
                  >
                    Remover
                  </button>
                </li>
              ))}
            </ul>
          )}
          <button
            type="button"
            className="mt-3 text-sm font-medium text-[#0f3d32]"
            onClick={() => onChange({ ...data, ptts: [...data.ptts, { ...PTT_VAZIO }] })}
          >
            Adicionar produto
          </button>
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

      {aviso ? <p className="text-sm text-red-800">{aviso}</p> : null}
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
          onClick={() => {
            if (!data.metadata.titulo.trim() || !data.metadata.autor.trim() || !data.metadata.ano.trim() || !data.metadata.local.trim()) {
              setAba("gerais");
              setAviso("Informe título, autor, ano e local.");
              return;
            }
            if (!data.metadata.orientador.trim()) {
              setAba("banca");
              setAviso("Informe o orientador.");
              return;
            }
            const avaliadorIncompleto = data.banca.some((membro, index) => {
              if (index === indiceOrientador || index === indiceCoorientador) return false;
              if (!ehAvaliador(funcaoCanonico(membro.funcao))) return false;
              return !membro.nome.trim() || !membro.instituicao.trim();
            });
            if (avaliadorIncompleto) {
              setAba("banca");
              setAviso("Preencha o nome e a instituição de cada avaliador.");
              return;
            }
            const impactoPendente = data.ptts.some((item) => !impactoSelecionado(item.impacto));
            if (impactoPendente) {
              setAba("ptts");
              setAviso("Selecione o impacto de cada produto: Alto, Médio ou Baixo.");
              return;
            }
            setAviso(null);
            onNext();
          }}
          className="inline-flex h-11 items-center rounded-md bg-[#0f3d32] px-5 text-sm font-medium text-white hover:bg-[#145244]"
        >
          Confirmar e Padronizar
        </button>
      </div>
    </div>
  );
}
