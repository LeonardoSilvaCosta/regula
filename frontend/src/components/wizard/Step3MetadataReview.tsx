"use client";

import { useEffect, useState } from "react";

import { Card } from "@/components/ui/Card";
import type { ArtigoQuadro, DocumentSections, ParseResponse, PTTItem } from "@/lib/api";
import { faixaImpacto } from "@/lib/ptt";
import type { components } from "@/types/api";

type Metadata = components["schemas"]["DocumentMetadata"];
type BancaMember = components["schemas"]["BancaMember"];

export const AREA_CONCENTRACAO_PADRAO = "Segurança Pública, Justiça, Conflitos e Cidadania";

export const LINHAS_PESQUISA = [
  "Políticas, Gestão, Direitos Humanos, Criminalidade e Tecnologia da Informação",
  "Segurança Pública, Criminologia e Sistema de Justiça Criminal",
] as const;

type LinhaPesquisa = (typeof LINHAS_PESQUISA)[number];

function linhaOficial(valor: string): LinhaPesquisa | "" {
  return LINHAS_PESQUISA.find((linha) => linha === valor) ?? "";
}

const ABAS = [
  { id: "gerais", label: "Dados gerais" },
  { id: "banca", label: "Orientação e banca" },
  { id: "secoes", label: "Seções do trabalho" },
  { id: "siglas", label: "Siglas" },
  { id: "ptts", label: "Produtos técnicos" },
  { id: "quadro", label: "Estrutura / Quadro 1" },
] as const;

type Aba = (typeof ABAS)[number]["id"];

const campo =
  "mt-1 w-full rounded-md border border-[#d9d1c3] bg-white px-3 py-2 text-sm outline-none focus:border-[#0f3d32]";

const TITULO_PLACEHOLDER = "ESTEIRA PREDITIVA MULTIMODAL DE SUPORTE À DECISÃO CLÍNICA NO CIAP/PMPA";
const SUBTITULO_PLACEHOLDER =
  "Modelos de aprendizado de máquina para predição de desfechos relacionados à saúde mental de policiais militares do Pará a partir de prontuários psicossociais";
const AUTOR_PLACEHOLDER = "Leonardo da Silva Costa";
const ANO_PLACEHOLDER = "2026";
const INSTITUICAO_ORIENTADOR_PLACEHOLDER = "Universidade Federal do Pará";
const COORDENADOR_PLACEHOLDER = "Prof. Dr. Edson Marcos Leal Soares Ramos";
const ORIENTADOR_PLACEHOLDER = "Prof. Dr. Renato Hidaka Torres";
const IMPACTOS = ["Alto", "Médio", "Baixo"] as const;
const INOVACOES = ["Alto", "Médio", "Baixo"] as const;
const COMPLEXIDADES = ["Alta", "Média", "Baixa"] as const;
const DEMANDAS = ["Espontânea", "Contratada", "Edital-concorrência"] as const;
const ABRANGENCIAS = ["Local", "Regional", "Nacional", "Internacional"] as const;
const STATUS_QUADRO = ["Em produção", "Concluído", "Submetido"] as const;
const TIPO_ESTUDO_PADRAO = "Qualitativo/Quantitativo Exploratório Descritivo";
const ROMANOS = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii"];
const LIMITE_PALAVRAS = 50;

const TIPOS_PTT = [
  { tipo: "Material Didático", subtipo: "Infográfico" },
  { tipo: "Software Registrável", subtipo: "Software" },
  { tipo: "Base de Dados", subtipo: "Base de Dados" },
  { tipo: "Manual/Protocolo", subtipo: "Codebook" },
] as const;

const CAMPOS_PARAGRAFOS = [
  "apresentacao",
  "introducao",
  "justificativa",
  "problema",
  "revisao",
  "referencial_teorico",
  "objetivos_especificos",
  "hipotese",
  "metodologia_natureza",
  "metodologia_fontes",
  "metodologia_coleta",
  "referencias",
] as const satisfies readonly (keyof DocumentSections)[];

type CampoParagrafos = (typeof CAMPOS_PARAGRAFOS)[number];

function paragrafosParaTexto(valor: string[] | undefined) {
  return (valor ?? []).join("\n\n");
}

function textoParaParagrafos(valor: string) {
  return valor
    .split("\n\n")
    .map((paragrafo) => paragrafo.trim())
    .filter(Boolean);
}

const PTT_VAZIO: PTTItem = {
  num: "",
  nome: "",
  autoria: "",
  tipo: "",
  subtipo: "",
  titulo: "",
  ano: null,
  coautoria: "",
  coautores: "",
  projeto: "",
  financiamento: "",
  financiador: "",
  demanda: "Espontânea",
  impacto: "Alto",
  justificativa_impacto: "",
  inovacao: "Alto",
  justificativa_inovacao: "",
  complexidade: "Alta",
  justificativa_complexidade: "",
  validacao: "",
  divulgacao: "",
  divulgacao_url: "",
  abrangencia: "Local",
  publico_usuario: "Estado, Município, Comunidade",
  objetivo_especifico: "",
  tipo_estudo: TIPO_ESTUDO_PADRAO,
  fontes: "",
  status: "Em produção",
};

const ARTIGO_VAZIO: ArtigoQuadro = {
  titulo: "",
  objetivo_especifico: "",
  tipo_estudo: TIPO_ESTUDO_PADRAO,
  fontes: "",
  status: "Em produção",
  subtipo: "Artigo",
};

function contarPalavras(texto: string) {
  const limpo = texto.trim();
  if (!limpo) return 0;
  return limpo.split(/\s+/).length;
}

function coautoriaDocente(orientador?: string, coorientador?: string) {
  return [orientador, coorientador]
    .map((nome) => (nome ?? "").trim())
    .filter(Boolean)
    .map((nome) => `${nome} - Docente`)
    .join("; ");
}

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

function Justificativa({
  rotulo,
  valor,
  onChange,
}: {
  rotulo: string;
  valor: string;
  onChange: (valor: string) => void;
}) {
  const palavras = contarPalavras(valor);
  const estourou = palavras > LIMITE_PALAVRAS;
  return (
    <label className="block text-xs text-[#6b645a]">
      {rotulo}
      <textarea
        rows={3}
        className={`mt-1 w-full rounded-md border px-2 py-1.5 text-sm ${estourou ? "border-red-700" : "border-[#d9d1c3]"}`}
        value={valor}
        onChange={(event) => onChange(event.target.value)}
      />
      <span className={`mt-1 block ${estourou ? "font-medium text-red-800" : "text-[#6b645a]"}`}>
        {palavras}/{LIMITE_PALAVRAS} palavras
        {estourou ? " — acima do limite da Resolução 007/2025" : ""}
      </span>
    </label>
  );
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

  useEffect(() => {
    if (data.metadata.area_concentracao === AREA_CONCENTRACAO_PADRAO) return;
    onChange({
      ...data,
      metadata: { ...data.metadata, area_concentracao: AREA_CONCENTRACAO_PADRAO },
    });
  }, [data, onChange]);

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

  function patchArtigo(index: number, partial: Partial<ArtigoQuadro>) {
    const artigos = (data.artigos ?? []).map((item, i) => (i === index ? { ...item, ...partial } : item));
    onChange({ ...data, artigos });
  }

  const fontesPadrao = (data.sections.metodologia_fontes ?? []).find((item) => item.trim())
    || data.sections.metodologia_locus
    || "SIAC";
  const objetivosLista = (data.sections.objetivos_especificos ?? [])
    .map((item) => item.replace(/^\s*\(?\s*(?:i{1,3}|iv|vi{0,3}|ix|x|\d+)\s*[\).\]]\s*/i, "").trim())
    .filter(Boolean);
  const artigosQuadro = data.artigos ?? [];
  const linhasQuadro = [
    ...artigosQuadro.map((item, index) => ({
      origem: `Artigo ${index + 1}`,
      objetivo: objetivosLista[index]
        ? `(${ROMANOS[index] ?? index + 1}) ${objetivosLista[index]}`
        : `(${ROMANOS[index] ?? index + 1}) ${item.objetivo_especifico}`,
      produto: `Artigo ${index + 1}: ${item.titulo}`,
      estudo: item.tipo_estudo || TIPO_ESTUDO_PADRAO,
      fontes: item.fontes || fontesPadrao,
      status: item.status || "Em produção",
    })),
    ...data.ptts.map((item, index) => {
      const ordem = artigosQuadro.length + index;
      const num = item.num || String(index + 1);
      return {
        origem: item.num || `PTT ${index + 1}`,
        objetivo: objetivosLista[ordem]
          ? `(${ROMANOS[ordem] ?? ordem + 1}) ${objetivosLista[ordem]}`
          : `(${ROMANOS[ordem] ?? ordem + 1}) ${item.objetivo_especifico || ""}`,
        produto: `${item.subtipo || item.tipo || "PTT"} ${num} – ${item.titulo || item.nome}`,
        estudo: item.tipo_estudo || TIPO_ESTUDO_PADRAO,
        fontes: item.fontes || fontesPadrao,
        status: item.status || "Em produção",
      };
    }),
  ];

  const sugestaoCoautoria = coautoriaDocente(data.metadata.orientador, data.metadata.coorientador);

  useEffect(() => {
    if (!sugestaoCoautoria) return;
    const ptts = data.ptts.map((item) => {
      if ((item.coautores || item.coautoria || "").trim()) return item;
      return { ...item, coautores: sugestaoCoautoria, coautoria: sugestaoCoautoria };
    });
    if (ptts.some((item, indice) => item !== data.ptts[indice])) {
      onChange({ ...data, ptts });
    }
  }, [data, onChange, sugestaoCoautoria]);

  function patchSection(chave: keyof DocumentSections, valor: string | string[] | boolean) {
    const sections = { ...data.sections, [chave]: valor };
    onChange({ ...data, sections });
  }

  function valorParagrafos(chave: CampoParagrafos) {
    const atual = data.sections?.[chave];
    return Array.isArray(atual) ? atual : [];
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
            <label className="text-sm sm:col-span-2">
              Área de concentração
              <input
                readOnly
                aria-readonly="true"
                className={`${campo} cursor-default bg-[#f7f4ee] text-[#4a453c]`}
                value={AREA_CONCENTRACAO_PADRAO}
              />
            </label>
            <label className="text-sm sm:col-span-2">
              Linha de pesquisa <span className="text-red-800">*</span>
              <select
                required
                className={campo}
                value={linhaOficial(data.metadata.linha_pesquisa)}
                onChange={(event) => patchMetadata({ linha_pesquisa: event.target.value })}
              >
                <option value="" disabled>
                  Selecione a linha de pesquisa
                </option>
                {LINHAS_PESQUISA.map((linha) => (
                  <option key={linha} value={linha}>
                    {linha}
                  </option>
                ))}
              </select>
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
              {(data.metadata.coorientador ?? "").trim() ? (
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

      {aba === "secoes" && (
        <Card title="Seções do trabalho">
          <div className="flex flex-col gap-3">
            <details open className="rounded-lg border border-[#efe8dc] p-3">
              <summary className="cursor-pointer text-sm font-semibold text-[#0f3d32]">
                Apresentação e contexto <span className="font-normal text-[#6b645a]">(opcional)</span>
              </summary>
              <label className="mt-3 block text-sm">
                Trajetória e percurso do autor
                <textarea
                  rows={5}
                  className={campo}
                  value={paragrafosParaTexto(valorParagrafos("apresentacao"))}
                  onChange={(event) => patchSection("apresentacao", textoParaParagrafos(event.target.value))}
                />
              </label>
            </details>

            <details open className="rounded-lg border border-[#efe8dc] p-3">
              <summary className="cursor-pointer text-sm font-semibold text-[#0f3d32]">1. Considerações gerais</summary>
              <div className="mt-3 flex flex-col gap-4">
                <label className="text-sm">
                  Contextualização e justificativa do tema
                  <textarea
                    rows={5}
                    className={campo}
                    value={paragrafosParaTexto(valorParagrafos("introducao"))}
                    onChange={(event) => patchSection("introducao", textoParaParagrafos(event.target.value))}
                  />
                </label>
                <label className="text-sm">
                  Relevância institucional e acadêmica
                  <textarea
                    rows={5}
                    className={campo}
                    value={paragrafosParaTexto(valorParagrafos("justificativa"))}
                    onChange={(event) => patchSection("justificativa", textoParaParagrafos(event.target.value))}
                  />
                </label>
                <label className="text-sm">
                  Problema de pesquisa / questão central
                  <textarea
                    rows={4}
                    className={campo}
                    value={paragrafosParaTexto(valorParagrafos("problema"))}
                    onChange={(event) => patchSection("problema", textoParaParagrafos(event.target.value))}
                  />
                </label>
                <label className="text-sm">
                  Revisão da literatura
                  <span className="block text-xs text-[#6b645a]">Seção 1.4. REVISÃO DA LITERATURA.</span>
                  <textarea
                    rows={5}
                    className={campo}
                    value={paragrafosParaTexto(valorParagrafos("revisao"))}
                    onChange={(event) => patchSection("revisao", textoParaParagrafos(event.target.value))}
                  />
                </label>
                <label className="flex items-start gap-2 text-sm">
                  <input
                    type="checkbox"
                    className="mt-1"
                    checked={Boolean(data.sections?.incluir_referencial_teorico)}
                    onChange={(event) => patchSection("incluir_referencial_teorico", event.target.checked)}
                  />
                  <span>
                    Incluir referencial teórico
                    <span className="block text-xs text-[#6b645a]">
                      A seção 1.4 passa a se chamar REVISÃO DA LITERATURA E REFERENCIAL TEÓRICO, com as subseções 1.4.1 e 1.4.2.
                    </span>
                  </span>
                </label>
                {data.sections?.incluir_referencial_teorico && (
                  <label className="text-sm">
                    Referencial teórico
                    <textarea
                      rows={5}
                      className={campo}
                      value={paragrafosParaTexto(valorParagrafos("referencial_teorico"))}
                      onChange={(event) => patchSection("referencial_teorico", textoParaParagrafos(event.target.value))}
                    />
                  </label>
                )}
              </div>
            </details>

            <details open className="rounded-lg border border-[#efe8dc] p-3">
              <summary className="cursor-pointer text-sm font-semibold text-[#0f3d32]">2. Objetivos</summary>
              <div className="mt-3 flex flex-col gap-4">
                <label className="text-sm">
                  Objetivo geral
                  <input
                    className={campo}
                    value={data.sections?.objetivo_geral ?? ""}
                    onChange={(event) => patchSection("objetivo_geral", event.target.value)}
                  />
                </label>
                <label className="text-sm">
                  Objetivos específicos
                  <span className="block text-xs text-[#6b645a]">Um objetivo por parágrafo. A lista numerada preenche a seção 2.2 e a coluna do Quadro 1, na mesma ordem dos artigos e produtos.</span>
                  <textarea
                    rows={5}
                    className={campo}
                    value={paragrafosParaTexto(valorParagrafos("objetivos_especificos"))}
                    onChange={(event) => patchSection("objetivos_especificos", textoParaParagrafos(event.target.value))}
                  />
                  {objetivosLista.length > 0 && (
                    <ol className="mt-2 list-none space-y-1 text-sm text-[#3d3832]">
                      {objetivosLista.map((item, index) => (
                        <li key={`${index}-${item.slice(0, 24)}`}>
                          ({ROMANOS[index] ?? index + 1}) {item}
                        </li>
                      ))}
                    </ol>
                  )}
                </label>
                <label className="flex items-start gap-2 text-sm">
                  <input
                    type="checkbox"
                    className="mt-1"
                    checked={Boolean(data.sections?.incluir_hipoteses)}
                    onChange={(event) => patchSection("incluir_hipoteses", event.target.checked)}
                  />
                  <span>
                    Incluir hipóteses ou questões norteadoras
                    <span className="block text-xs text-[#6b645a]">
                      Seção opcional. Quando marcada, entra depois dos objetivos e desloca a numeração seguinte.
                    </span>
                  </span>
                </label>
                {data.sections?.incluir_hipoteses && (
                  <label className="text-sm">
                    Hipóteses ou questões norteadoras
                    <textarea
                      rows={4}
                      className={campo}
                      value={paragrafosParaTexto(valorParagrafos("hipotese"))}
                      onChange={(event) => patchSection("hipotese", textoParaParagrafos(event.target.value))}
                    />
                  </label>
                )}
              </div>
            </details>

            <details open className="rounded-lg border border-[#efe8dc] p-3">
              <summary className="cursor-pointer text-sm font-semibold text-[#0f3d32]">4. Metodologia</summary>
              <div className="mt-3 flex flex-col gap-4">
                <label className="text-sm">
                  Tipo e tipificação da pesquisa
                  <textarea
                    rows={4}
                    className={campo}
                    value={paragrafosParaTexto(valorParagrafos("metodologia_natureza"))}
                    onChange={(event) => patchSection("metodologia_natureza", textoParaParagrafos(event.target.value))}
                  />
                </label>
                <label className="text-sm">
                  Lócus institucional
                  <textarea
                    rows={3}
                    className={campo}
                    value={data.sections?.metodologia_locus ?? ""}
                    onChange={(event) => patchSection("metodologia_locus", event.target.value)}
                  />
                </label>
                <label className="text-sm">
                  Universo e amostragem
                  <span className="block text-xs text-[#6b645a]">Um parágrafo por linha em branco.</span>
                  <textarea
                    rows={8}
                    className={campo}
                    value={paragrafosParaTexto(valorParagrafos("metodologia_participantes"))}
                    onChange={(event) =>
                      patchSection("metodologia_participantes", textoParaParagrafos(event.target.value))
                    }
                  />
                </label>
                <label className="text-sm">
                  Fontes de dados
                  <textarea
                    rows={4}
                    className={campo}
                    value={paragrafosParaTexto(valorParagrafos("metodologia_fontes"))}
                    onChange={(event) => patchSection("metodologia_fontes", textoParaParagrafos(event.target.value))}
                  />
                </label>
                <label className="text-sm">
                  Procedimentos de coleta/mineração
                  <textarea
                    rows={4}
                    className={campo}
                    value={paragrafosParaTexto(valorParagrafos("metodologia_coleta"))}
                    onChange={(event) => patchSection("metodologia_coleta", textoParaParagrafos(event.target.value))}
                  />
                </label>
                <label className="text-sm">
                  Salvaguardas éticas e LGPD
                  <textarea
                    rows={6}
                    className={campo}
                    value={paragrafosParaTexto(valorParagrafos("metodologia_etica"))}
                    onChange={(event) => patchSection("metodologia_etica", textoParaParagrafos(event.target.value))}
                  />
                </label>
                <label className="text-sm">
                  Análise de dados e modelagem
                  <textarea
                    rows={8}
                    className={campo}
                    value={paragrafosParaTexto(valorParagrafos("metodologia_analise"))}
                    onChange={(event) =>
                      patchSection("metodologia_analise", textoParaParagrafos(event.target.value))
                    }
                  />
                </label>
              </div>
            </details>

            <details open className="rounded-lg border border-[#efe8dc] p-3">
              <summary className="cursor-pointer text-sm font-semibold text-[#0f3d32]">Referências</summary>
              <label className="mt-3 block text-sm">
                Lista de referências em normas ABNT
                <span className="block text-xs text-[#6b645a]">Uma referência por parágrafo.</span>
                <textarea
                  rows={8}
                  className={campo}
                  value={paragrafosParaTexto(valorParagrafos("referencias"))}
                  onChange={(event) => patchSection("referencias", textoParaParagrafos(event.target.value))}
                />
              </label>
            </details>
          </div>
        </Card>
      )}

      {aba === "ptts" && (
        <Card title="Produtos técnicos (PTTs)">
          {data.ptts.length === 0 ? (
            <p className="text-sm text-[#5c564c]">Nenhum produto técnico foi extraído.</p>
          ) : (
            <ul className="flex flex-col gap-4">
              {data.ptts.map((item, index) => {
                const coautores = item.coautores || item.coautoria;
                const divulgacao = item.divulgacao_url || item.divulgacao;
                return (
                  <li key={`${item.num}-${index}`} className="rounded-lg border border-[#efe8dc] p-3">
                    <div className="mb-2 flex items-center justify-between gap-3">
                      <p className="text-sm font-semibold text-[#0f3d32]">{item.num || `PTT ${index + 1}`}</p>
                      <button
                        type="button"
                        className="text-sm text-red-800"
                        onClick={() => onChange({ ...data, ptts: data.ptts.filter((_, i) => i !== index) })}
                      >
                        Remover
                      </button>
                    </div>
                    <div className="flex flex-col gap-3">
                      <details open className="rounded-lg border border-[#efe8dc] p-3">
                        <summary className="cursor-pointer text-sm font-semibold text-[#0f3d32]">Dados Básicos</summary>
                        <div className="mt-3 grid gap-2 sm:grid-cols-2">
                          <p className="text-xs text-[#6b645a] sm:col-span-2">
                            Autoria, área, linha e projeto saem dos dados gerais quando ficam em branco aqui.
                            Autoria atual: {data.metadata.autor || "—"}.
                          </p>
                          <label className="text-xs text-[#6b645a] sm:col-span-2">
                            Título
                            <input
                              aria-label="Título do produto"
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              value={item.titulo || item.nome}
                              onChange={(event) => patchPtt(index, { titulo: event.target.value, nome: event.target.value })}
                            />
                          </label>
                          <label className="text-xs text-[#6b645a] sm:col-span-2">
                            Objetivo específico vinculado
                            <textarea
                              rows={2}
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              value={item.objetivo_especifico || ""}
                              onChange={(event) => patchPtt(index, { objetivo_especifico: event.target.value })}
                            />
                          </label>
                          <label className="text-xs text-[#6b645a]">
                            Tipo de estudo
                            <input
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              value={item.tipo_estudo || TIPO_ESTUDO_PADRAO}
                              onChange={(event) => patchPtt(index, { tipo_estudo: event.target.value })}
                            />
                          </label>
                          <label className="text-xs text-[#6b645a]">
                            Fontes
                            <input
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              placeholder={fontesPadrao}
                              value={item.fontes || ""}
                              onChange={(event) => patchPtt(index, { fontes: event.target.value })}
                            />
                          </label>
                          <label className="text-xs text-[#6b645a]">
                            Status
                            <select
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              value={item.status || "Em produção"}
                              onChange={(event) => patchPtt(index, { status: event.target.value })}
                            >
                              {STATUS_QUADRO.map((valor) => (
                                <option key={valor} value={valor}>
                                  {valor}
                                </option>
                              ))}
                            </select>
                          </label>
                          <label className="text-xs text-[#6b645a]">
                            Tipo
                            <select
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              value={item.tipo}
                              onChange={(event) => {
                                const par = TIPOS_PTT.find((opcao) => opcao.tipo === event.target.value);
                                patchPtt(index, { tipo: event.target.value, subtipo: par?.subtipo ?? item.subtipo });
                              }}
                            >
                              <option value="">Selecione</option>
                              {item.tipo && !TIPOS_PTT.some((opcao) => opcao.tipo === item.tipo) ? (
                                <option value={item.tipo}>{item.tipo}</option>
                              ) : null}
                              {TIPOS_PTT.map((opcao) => (
                                <option key={opcao.tipo} value={opcao.tipo}>
                                  {opcao.tipo}
                                </option>
                              ))}
                            </select>
                          </label>
                          <label className="text-xs text-[#6b645a]">
                            Subtipo
                            <select
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              value={item.subtipo}
                              onChange={(event) => patchPtt(index, { subtipo: event.target.value })}
                            >
                              <option value="">Selecione</option>
                              {item.subtipo && !TIPOS_PTT.some((opcao) => opcao.subtipo === item.subtipo) ? (
                                <option value={item.subtipo}>{item.subtipo}</option>
                              ) : null}
                              {TIPOS_PTT.map((opcao) => (
                                <option key={opcao.subtipo} value={opcao.subtipo}>
                                  {opcao.subtipo}
                                </option>
                              ))}
                            </select>
                          </label>
                          <label className="text-xs text-[#6b645a]">
                            Ano
                            <input
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              placeholder={data.metadata.ano || "Ano do trabalho"}
                              value={item.ano ?? ""}
                              onChange={(event) => patchPtt(index, { ano: event.target.value || null })}
                            />
                          </label>
                          <label className="text-xs text-[#6b645a]">
                            Demanda
                            <select
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              value={item.demanda || "Espontânea"}
                              onChange={(event) => patchPtt(index, { demanda: event.target.value })}
                            >
                              {DEMANDAS.map((valor) => (
                                <option key={valor} value={valor}>
                                  {valor}
                                </option>
                              ))}
                            </select>
                          </label>
                          <label className="text-xs text-[#6b645a] sm:col-span-2">
                            Coautoria e categoria
                            <input
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              placeholder="Nome Orientador - Docente"
                              value={coautores}
                              onChange={(event) =>
                                patchPtt(index, { coautores: event.target.value, coautoria: event.target.value })
                              }
                            />
                          </label>
                          <label className="text-xs text-[#6b645a] sm:col-span-2">
                            Projeto de pesquisa
                            <input
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              placeholder={data.metadata.titulo}
                              value={item.projeto}
                              onChange={(event) => patchPtt(index, { projeto: event.target.value })}
                            />
                          </label>
                          <label className="text-xs text-[#6b645a]">
                            Financiamento
                            <input
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              value={item.financiamento}
                              onChange={(event) => patchPtt(index, { financiamento: event.target.value })}
                            />
                          </label>
                          <label className="text-xs text-[#6b645a]">
                            Financiador
                            <input
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              value={item.financiador}
                              onChange={(event) => patchPtt(index, { financiador: event.target.value })}
                            />
                          </label>
                        </div>
                      </details>

                      <details className="rounded-lg border border-[#efe8dc] p-3">
                        <summary className="cursor-pointer text-sm font-semibold text-[#0f3d32]">
                          Avaliação Técnica - 50 palavras
                        </summary>
                        <div className="mt-3 grid gap-3">
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
                          <Justificativa
                            rotulo="Justificativa do impacto"
                            valor={item.justificativa_impacto}
                            onChange={(valor) => patchPtt(index, { justificativa_impacto: valor })}
                          />
                          <label className="text-xs text-[#6b645a]">
                            Inovação
                            <select
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              value={item.inovacao || "Alto"}
                              onChange={(event) => patchPtt(index, { inovacao: event.target.value })}
                            >
                              {INOVACOES.map((valor) => (
                                <option key={valor} value={valor}>
                                  {valor}
                                </option>
                              ))}
                            </select>
                          </label>
                          <Justificativa
                            rotulo="Justificativa da inovação"
                            valor={item.justificativa_inovacao}
                            onChange={(valor) => patchPtt(index, { justificativa_inovacao: valor })}
                          />
                          <label className="text-xs text-[#6b645a]">
                            Complexidade
                            <select
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              value={item.complexidade || "Alta"}
                              onChange={(event) => patchPtt(index, { complexidade: event.target.value })}
                            >
                              {COMPLEXIDADES.map((valor) => (
                                <option key={valor} value={valor}>
                                  {valor}
                                </option>
                              ))}
                            </select>
                          </label>
                          <Justificativa
                            rotulo="Justificativa da complexidade"
                            valor={item.justificativa_complexidade}
                            onChange={(valor) => patchPtt(index, { justificativa_complexidade: valor })}
                          />
                        </div>
                      </details>

                      <details className="rounded-lg border border-[#efe8dc] p-3">
                        <summary className="cursor-pointer text-sm font-semibold text-[#0f3d32]">Validação e Inserção</summary>
                        <div className="mt-3 grid gap-2 sm:grid-cols-2">
                          <label className="text-xs text-[#6b645a] sm:col-span-2">
                            Validação do produto
                            <input
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              placeholder="Publicado no Portal EduCapes, Registro INPI"
                              value={item.validacao}
                              onChange={(event) => patchPtt(index, { validacao: event.target.value })}
                            />
                          </label>
                          <label className="text-xs text-[#6b645a] sm:col-span-2">
                            Modo de divulgação
                            <input
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              placeholder="https://"
                              value={divulgacao}
                              onChange={(event) =>
                                patchPtt(index, { divulgacao_url: event.target.value, divulgacao: event.target.value })
                              }
                            />
                          </label>
                          <label className="text-xs text-[#6b645a]">
                            Abrangência
                            <select
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              value={item.abrangencia || "Local"}
                              onChange={(event) => patchPtt(index, { abrangencia: event.target.value })}
                            >
                              {ABRANGENCIAS.map((valor) => (
                                <option key={valor} value={valor}>
                                  {valor}
                                </option>
                              ))}
                            </select>
                          </label>
                          <label className="text-xs text-[#6b645a]">
                            Público usuário
                            <input
                              className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                              value={item.publico_usuario}
                              onChange={(event) => patchPtt(index, { publico_usuario: event.target.value })}
                            />
                          </label>
                        </div>
                      </details>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
          <button
            type="button"
            className="mt-3 text-sm font-medium text-[#0f3d32]"
            onClick={() =>
              onChange({
                ...data,
                ptts: [
                  ...data.ptts,
                  {
                    ...PTT_VAZIO,
                    autoria: data.metadata.autor,
                    ano: data.metadata.ano || null,
                    coautores: sugestaoCoautoria,
                    coautoria: sugestaoCoautoria,
                    impacto: "Alto",
                    inovacao: "Alto",
                    complexidade: "Alta",
                    demanda: "Espontânea",
                    abrangencia: "Local",
                    publico_usuario: "Estado, Município, Comunidade",
                    projeto: data.metadata.titulo,
                  },
                ],
              })
            }
          >
            Adicionar produto
          </button>
        </Card>
      )}

      {aba === "quadro" && (
        <Card title="Estrutura / Quadro 1">
          <p className="mb-3 text-sm text-[#5c564c]">
            Cada artigo e cada produto técnico vira uma linha. Título e objetivo geral se repetem e serão mesclados no Word.
            Fontes em branco herdam {fontesPadrao}.
          </p>
          <ul className="mb-4 flex flex-col gap-3">
            {artigosQuadro.map((item, index) => (
              <li key={`artigo-${index}`} className="rounded-lg border border-[#efe8dc] p-3">
                <div className="mb-2 flex items-center justify-between">
                  <p className="text-sm font-semibold text-[#0f3d32]">Artigo {index + 1}</p>
                  <button
                    type="button"
                    className="text-sm text-red-800"
                    onClick={() => onChange({ ...data, artigos: artigosQuadro.filter((_, i) => i !== index) })}
                  >
                    Remover
                  </button>
                </div>
                <div className="grid gap-2 sm:grid-cols-2">
                  <label className="text-xs text-[#6b645a] sm:col-span-2">
                    Título do artigo
                    <input
                      className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                      value={item.titulo}
                      onChange={(event) => patchArtigo(index, { titulo: event.target.value })}
                    />
                  </label>
                  <label className="text-xs text-[#6b645a] sm:col-span-2">
                    Objetivo específico
                    <textarea
                      rows={2}
                      className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                      value={item.objetivo_especifico}
                      onChange={(event) => patchArtigo(index, { objetivo_especifico: event.target.value })}
                    />
                  </label>
                  <label className="text-xs text-[#6b645a]">
                    Tipo de estudo
                    <input
                      className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                      value={item.tipo_estudo || TIPO_ESTUDO_PADRAO}
                      onChange={(event) => patchArtigo(index, { tipo_estudo: event.target.value })}
                    />
                  </label>
                  <label className="text-xs text-[#6b645a]">
                    Fontes
                    <input
                      className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                      placeholder={fontesPadrao}
                      value={item.fontes}
                      onChange={(event) => patchArtigo(index, { fontes: event.target.value })}
                    />
                  </label>
                  <label className="text-xs text-[#6b645a]">
                    Status
                    <select
                      className="mt-1 w-full rounded-md border border-[#d9d1c3] px-2 py-1.5 text-sm"
                      value={item.status || "Em produção"}
                      onChange={(event) => patchArtigo(index, { status: event.target.value })}
                    >
                      {STATUS_QUADRO.map((valor) => (
                        <option key={valor} value={valor}>
                          {valor}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
              </li>
            ))}
          </ul>
          <button
            type="button"
            className="text-sm font-medium text-[#0f3d32]"
            onClick={() => onChange({ ...data, artigos: [...artigosQuadro, { ...ARTIGO_VAZIO }] })}
          >
            Adicionar artigo
          </button>
          <h3 className="mb-2 mt-6 text-sm font-semibold text-[#0f3d32]">Pré-visualização das linhas</h3>
          <div className="w-full min-w-0">
            <table className="w-full table-fixed border-collapse text-left text-xs">
              <colgroup>
                {[12, 16, 24, 22, 10, 6, 7].map((pct, index) => (
                  <col key={index} style={{ width: `${pct}%` }} />
                ))}
              </colgroup>
              <thead>
                <tr>
                  {["Título", "Objetivo Geral", "Objetivos Específicos", "Tipo de Produto", "Tipo de Estudo", "Fontes", "Status"].map((coluna) => (
                    <th key={coluna} className="border border-[#d9d1c3] bg-[#f6f1e8] px-2 py-1 font-semibold break-words">
                      {coluna}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {linhasQuadro.length === 0 ? (
                  <tr>
                    <td className="border border-[#d9d1c3] px-2 py-2 text-[#6b645a]" colSpan={7}>
                      Cadastre um artigo ou um produto técnico para gerar o Quadro 1.
                    </td>
                  </tr>
                ) : (
                  linhasQuadro.map((linha, index) => (
                    <tr key={`${linha.origem}-${index}`}>
                      <td className="border border-[#d9d1c3] px-2 py-1 align-top break-words">{data.metadata.titulo}</td>
                      <td className="border border-[#d9d1c3] px-2 py-1 align-top break-words">{data.sections.objetivo_geral}</td>
                      <td className="border border-[#d9d1c3] px-2 py-1 align-top break-words">{linha.objetivo}</td>
                      <td className="border border-[#d9d1c3] px-2 py-1 align-top break-words">{linha.produto}</td>
                      <td className="border border-[#d9d1c3] px-2 py-1 align-top break-words">{linha.estudo}</td>
                      <td className="border border-[#d9d1c3] px-2 py-1 align-top break-words">{linha.fontes}</td>
                      <td className="border border-[#d9d1c3] px-2 py-1 align-top break-words">{linha.status}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
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
            if (!linhaOficial(data.metadata.linha_pesquisa)) {
              setAba("gerais");
              setAviso("Selecione a linha de pesquisa do PPGSP/UFPA.");
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
