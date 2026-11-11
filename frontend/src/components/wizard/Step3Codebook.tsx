"use client";

import type { ReactNode } from "react";

import { codebookVazio, linhas, texto, type CategoriaCodebook, type Codebook, type MatrizFronteira } from "@/lib/codebook";
import type { ParseResponse } from "@/lib/api";

const campo =
  "mt-1 w-full rounded-md border border-[#d9d1c3] bg-white px-3 py-2 text-sm outline-none focus:border-[#0f3d32]";

export function Step3Codebook({
  data,
  onChange,
  onBack,
  onNext,
}: {
  data: ParseResponse;
  onChange: (next: ParseResponse) => void;
  onBack: () => void;
  onNext: () => void;
}) {
  const manual = data.codebook ?? codebookVazio();

  function atualizar(parcial: Partial<Codebook>) {
    onChange({ ...data, codebook: { ...manual, ...parcial } });
  }

  function atualizarCategoria(indice: number, parcial: Partial<CategoriaCodebook>) {
    const categorias = manual.categorias.map((item, posicao) =>
      posicao === indice ? { ...item, ...parcial } : item,
    );
    atualizar({ categorias });
  }

  function atualizarMatriz(indice: number, parcial: Partial<MatrizFronteira>) {
    const matrizes = manual.matrizes.map((item, posicao) =>
      posicao === indice ? { ...item, ...parcial } : item,
    );
    atualizar({ matrizes });
  }

  return (
    <form
      className="flex flex-col gap-5"
      onSubmit={(event) => {
        event.preventDefault();
        onNext();
      }}
    >
      <section className="rounded-xl border border-[#e4dccf] bg-white p-5">
        <h2 className="text-base font-medium">Capa e folha de rosto</h2>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <label className="text-sm sm:col-span-2">
            Título
            <input
              className={campo}
              value={data.metadata.titulo}
              onChange={(event) =>
                onChange({ ...data, metadata: { ...data.metadata, titulo: event.target.value } })
              }
            />
          </label>
          <label className="text-sm">
            Autor
            <input
              className={campo}
              value={data.metadata.autor}
              onChange={(event) =>
                onChange({ ...data, metadata: { ...data.metadata, autor: event.target.value } })
              }
            />
          </label>
          <label className="text-sm">
            Ano
            <input
              className={campo}
              value={data.metadata.ano}
              onChange={(event) =>
                onChange({ ...data, metadata: { ...data.metadata, ano: event.target.value } })
              }
            />
          </label>
        </div>
      </section>

      <Secao titulo="1. Identificação e metadados">
        <Area label="Contexto do projeto" value={texto(manual.contexto)} onChange={(valor) => atualizar({ contexto: linhas(valor) })} />
        <Area label="Autores e peritos (um por linha)" value={texto(manual.autores_peritos)} onChange={(valor) => atualizar({ autores_peritos: linhas(valor) })} />
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="text-sm">
            Versão corrente
            <input className={campo} value={manual.versao} onChange={(event) => atualizar({ versao: event.target.value })} />
          </label>
          <label className="text-sm">
            Data
            <input className={campo} value={manual.data_versao} onChange={(event) => atualizar({ data_versao: event.target.value })} />
          </label>
        </div>
        <Area label="Fontes de dados (uma por linha)" value={texto(manual.fontes_dados)} onChange={(valor) => atualizar({ fontes_dados: linhas(valor) })} />
        <Area label="Fundamentação teórica e normativa" value={texto(manual.fundamentacao)} onChange={(valor) => atualizar({ fundamentacao: linhas(valor) })} />
      </Secao>

      <Secao titulo="2. Governança ética e segurança">
        <Area label="Desidentificação e anonimização (LGPD/HIPAA)" value={texto(manual.desidentificacao)} onChange={(valor) => atualizar({ desidentificacao: linhas(valor) })} />
        <Area label="Aprovação em comitês de ética" value={texto(manual.aprovacao_etica)} onChange={(valor) => atualizar({ aprovacao_etica: linhas(valor) })} />
        <Area label="Salvaguardas de uso dos dados" value={texto(manual.salvaguardas)} onChange={(valor) => atualizar({ salvaguardas: linhas(valor) })} />
      </Secao>

      <Secao titulo="3. Regras de interpretação e segmentação">
        <Area label="Polaridade" value={texto(manual.polaridade)} onChange={(valor) => atualizar({ polaridade: linhas(valor) })} />
        <Area label="Sujeito da ação" value={texto(manual.sujeito)} onChange={(valor) => atualizar({ sujeito: linhas(valor) })} />
        <Area label="Temporalidade" value={texto(manual.temporalidade)} onChange={(valor) => atualizar({ temporalidade: linhas(valor) })} />
        <Area label="Granularidade sintagmática" value={texto(manual.granularidade)} onChange={(valor) => atualizar({ granularidade: linhas(valor) })} />
      </Secao>

      <Secao titulo="4. Fichas técnicas das categorias">
        {manual.categorias.map((categoria, indice) => (
          <div key={indice} className="rounded-lg border border-[#e4dccf] p-3">
            <div className="grid gap-3 sm:grid-cols-3">
              <label className="text-sm">
                Eixo
                <input className={campo} value={categoria.eixo} onChange={(event) => atualizarCategoria(indice, { eixo: event.target.value })} />
              </label>
              <label className="text-sm">
                Código
                <input className={campo} value={categoria.codigo} onChange={(event) => atualizarCategoria(indice, { codigo: event.target.value })} />
              </label>
              <label className="text-sm">
                Nome
                <input className={campo} value={categoria.nome} onChange={(event) => atualizarCategoria(indice, { nome: event.target.value })} />
              </label>
            </div>
            <Area label="Definição" value={categoria.definicao} onChange={(valor) => atualizarCategoria(indice, { definicao: valor })} />
            <Area label="Inclusão (uma por linha)" value={texto(categoria.inclusao)} onChange={(valor) => atualizarCategoria(indice, { inclusao: linhas(valor) })} />
            <Area label="Exclusão (uma por linha)" value={texto(categoria.exclusao)} onChange={(valor) => atualizarCategoria(indice, { exclusao: linhas(valor) })} />
            <Area label="Contraexemplos (um por linha)" value={texto(categoria.contraexemplos)} onChange={(valor) => atualizarCategoria(indice, { contraexemplos: linhas(valor) })} />
          </div>
        ))}
        <button
          type="button"
          className="text-sm text-[#0f3d32]"
          onClick={() =>
            atualizar({
              categorias: [
                ...manual.categorias,
                { eixo: "", codigo: "", nome: "", definicao: "", inclusao: [], exclusao: [], contraexemplos: [] },
              ],
            })
          }
        >
          Adicionar categoria
        </button>
      </Secao>

      <Secao titulo="5. Matrizes de fronteira e decisão">
        {manual.matrizes.map((matriz, indice) => (
          <div key={indice} className="rounded-lg border border-[#e4dccf] p-3">
            <label className="text-sm">
              Título do quadro
              <input className={campo} value={matriz.titulo} onChange={(event) => atualizarMatriz(indice, { titulo: event.target.value })} />
            </label>
            <Area
              label="Colunas, separadas por |"
              value={matriz.colunas.join(" | ")}
              onChange={(valor) => atualizarMatriz(indice, { colunas: valor.split("|").map((item) => item.trim()).filter(Boolean) })}
            />
            <Area
              label="Linhas (uma por linha, células separadas por |)"
              value={matriz.linhas.map((linha) => linha.join(" | ")).join("\n")}
              onChange={(valor) =>
                atualizarMatriz(indice, {
                  linhas: linhas(valor).map((linha) => linha.split("|").map((item) => item.trim())),
                })
              }
            />
          </div>
        ))}
        <button
          type="button"
          className="text-sm text-[#0f3d32]"
          onClick={() =>
            atualizar({
              matrizes: [
                ...manual.matrizes,
                { titulo: "", colunas: ["Situação limítrofe", "Regra de desempate"], linhas: [], fonte: "Construção do(a) autor(a)." },
              ],
            })
          }
        >
          Adicionar quadro
        </button>
      </Secao>

      <Secao titulo="6. Protocolo de confiabilidade e adjudicação">
        <Area label="Métricas (κ, α)" value={texto(manual.metricas)} onChange={(valor) => atualizar({ metricas: linhas(valor) })} />
        <Area
          label="Limiares (métrica | limiar, um por linha)"
          value={texto(manual.limiares)}
          onChange={(valor) => atualizar({ limiares: linhas(valor) })}
        />
        <Area label="Fase piloto" value={texto(manual.adjudicacao_piloto)} onChange={(valor) => atualizar({ adjudicacao_piloto: linhas(valor) })} />
        <Area label="Produção" value={texto(manual.adjudicacao_producao)} onChange={(valor) => atualizar({ adjudicacao_producao: linhas(valor) })} />
      </Secao>

      <Secao titulo="7. Especificação operacional e governança">
        <label className="text-sm">
          Ferramenta
          <input className={campo} value={manual.ferramenta} onChange={(event) => atualizar({ ferramenta: event.target.value })} />
        </label>
        <Area
          label="Configuração XML ou JSON"
          value={manual.configuracao_interface}
          onChange={(valor) => atualizar({ configuracao_interface: valor })}
        />
        <Area label="Histórico de versões (um item por linha)" value={texto(manual.changelog)} onChange={(valor) => atualizar({ changelog: linhas(valor) })} />
      </Secao>

      <Secao titulo="Listas e referências">
        <Area
          label="Siglas (SIGLA | significado)"
          value={data.siglas.map((par) => par.join(" | ")).join("\n")}
          onChange={(valor) =>
            onChange({
              ...data,
              siglas: linhas(valor).map((linha) => {
                const [sigla, ...resto] = linha.split("|");
                return [sigla.trim(), resto.join("|").trim()];
              }),
            })
          }
        />
        <Area
          label="Símbolos (símbolo | significado)"
          value={manual.simbolos.map((par) => par.join(" | ")).join("\n")}
          onChange={(valor) =>
            atualizar({
              simbolos: linhas(valor).map((linha) => {
                const [simbolo, ...resto] = linha.split("|");
                return [simbolo.trim(), resto.join("|").trim()];
              }),
            })
          }
        />
        <Area
          label="Referências (uma por linha)"
          value={texto(data.sections.referencias)}
          onChange={(valor) =>
            onChange({ ...data, sections: { ...data.sections, referencias: linhas(valor) }, codebook: manual })
          }
        />
      </Secao>

      <div className="flex justify-between">
        <button type="button" className="rounded-lg border border-[#d9d1c3] px-4 py-2 text-sm" onClick={onBack}>
          Voltar
        </button>
        <button type="submit" className="rounded-lg bg-[#0f3d32] px-4 py-2 text-sm text-white">
          Continuar
        </button>
      </div>
    </form>
  );
}

function Secao({ titulo, children }: { titulo: string; children: ReactNode }) {
  return (
    <section className="flex flex-col gap-3 rounded-xl border border-[#e4dccf] bg-white p-5">
      <h2 className="text-base font-medium">{titulo}</h2>
      {children}
    </section>
  );
}

function Area({ label, value, onChange }: { label: string; value: string; onChange: (valor: string) => void }) {
  return (
    <label className="text-sm">
      {label}
      <textarea className={`${campo} min-h-24`} value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}
