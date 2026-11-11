"""Manual de Codificação Operacional e Rotulagem de Prontuários (Codebook)."""
import docx
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

from core.atualizar_campos import atualizar_campos_word
from core.campos import adicionar_bookmark
from core.styles import (
    apply_base_styles,
    aplicar_cabecalho_institucional,
    aplicar_idioma_pt_br,
    aplicar_rodape_local_ano,
    limpar_rodape,
)
from core.xml_utils import aplicar_autoajuste_janela, set_cell_border
from generators.common.referencias import renderizar_referencias
from generators.common.tabelas import inserir_tabela
from generators.qualificacao.builder import _paginar, _secao_sem_numero, habilitar_atualizacao_campos
from generators.qualificacao.formato import adicionar_lacuna, adicionar_paragrafo, adicionar_titulo
from generators.qualificacao.pre_textual.capa import build_capa
from generators.qualificacao.pre_textual.folha_rosto import build_folha_rosto
from generators.qualificacao.pre_textual.listas_ilustracoes import build_lista_ilustracoes
from generators.qualificacao.pre_textual.listas_siglas import build_lista_siglas, normalizar_siglas
from generators.qualificacao.pre_textual.sumario import build_sumario
from generators.common.subscrito import escrever_com_subscrito
from generators.qualificacao.pre_textual.simbolos import build_lista_simbolos

TEXTO_NATUREZA = (
    "Manual de Codificação Operacional e Rotulagem de Prontuários (Codebook) apresentado ao "
    "Programa de Pós-Graduação em Segurança Pública, da Universidade Federal do Pará, como produto "
    "técnico vinculado à pesquisa de mestrado."
)


def _lista(valor):
    if valor is None:
        return []
    if isinstance(valor, (list, tuple)):
        return [str(item).strip() for item in valor if str(item).strip()]
    texto = str(valor).strip()
    return [texto] if texto else []


def _estilizar_corpo(run, _subscrito):
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)


def _paragrafo(doc, texto):
    p = adicionar_paragrafo(doc, "")
    if p.runs:
        p.runs[0]._element.getparent().remove(p.runs[0]._element)
    escrever_com_subscrito(p, texto, _estilizar_corpo)
    return p


def _corpo(doc, valor):
    paragrafos = _lista(valor)
    if not paragrafos:
        adicionar_lacuna(doc, "[Preencher]")
        return
    for paragrafo in paragrafos:
        _paragrafo(doc, paragrafo)


def _itens(doc, valor):
    paragrafos = _lista(valor)
    if not paragrafos:
        adicionar_lacuna(doc, "[Preencher]")
        return
    for paragrafo in paragrafos:
        p = _paragrafo(doc, paragrafo)
        p.paragraph_format.left_indent = Cm(0.75)
        p.paragraph_format.first_line_indent = Cm(0)


def _celula(celula, texto, negrito=False):
    celula.text = ""
    celula.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = celula.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    def estilizar(run, _subscrito):
        run.bold = negrito
        run.font.name = "Times New Roman"
        run.font.size = Pt(10)

    escrever_com_subscrito(p, texto, estilizar)
    set_cell_border(celula, top={"sz": 4}, bottom={"sz": 4}, left={"sz": 4}, right={"sz": 4})


def _quadro(doc, numero, titulo, colunas, linhas, fonte, bookmark):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(f"Quadro {numero} – {titulo}")
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    adicionar_bookmark(p, bookmark)

    colunas = [str(coluna) for coluna in colunas] or ["Critério", "Decisão"]
    linhas = [["" if valor is None else str(valor) for valor in linha] for linha in linhas]
    if not linhas:
        linhas = [[""] * len(colunas)]
    largura = max(len(colunas), max(len(linha) for linha in linhas))
    while len(colunas) < largura:
        colunas.append("")
    tabela = doc.add_table(rows=1 + len(linhas), cols=largura)
    tabela.alignment = WD_TABLE_ALIGNMENT.CENTER
    aplicar_autoajuste_janela(tabela)
    for indice, nome in enumerate(colunas):
        _celula(tabela.rows[0].cells[indice], nome, negrito=True)
    for r_idx, linha in enumerate(linhas, start=1):
        for c_idx in range(largura):
            valor = linha[c_idx] if c_idx < len(linha) else ""
            _celula(tabela.rows[r_idx].cells[c_idx], valor)
    p_fonte = doc.add_paragraph()
    p_fonte.paragraph_format.space_before = Pt(2)
    p_fonte.paragraph_format.space_after = Pt(12)
    p_fonte.paragraph_format.line_spacing = 1.0
    r_fonte = p_fonte.add_run(f"Fonte: {fonte}")
    r_fonte.font.name = "Times New Roman"
    r_fonte.font.size = Pt(10)


def _ilustracoes(matrizes):
    quadros = []
    for indice, matriz in enumerate(matrizes, start=1):
        titulo = str(matriz.get("titulo") or f"Matriz de fronteira {indice}").strip()
        quadros.append(
            {
                "rotulo": "Quadro",
                "numero": indice,
                "titulo": titulo,
                "bookmark": f"cb_quadro_{indice}",
                "origem": "Matrizes de fronteira",
            }
        )
    return {"quadros": quadros, "tabelas": []}


def gerar_documento_codebook(caminho_saida, revisao=None, nivel="mestrado", assets_dir="assets"):
    dados = revisao or {}
    meta = dict(dados.get("metadata") or {})
    meta["nivel"] = str(nivel or meta.get("nivel") or "mestrado").strip().lower()
    secoes = dict(dados.get("sections") or {})
    manual = dict(dados.get("codebook") or {})
    pares_siglas = normalizar_siglas(dados.get("siglas") or meta.get("siglas"))
    simbolos = list(manual.get("simbolos") or [])
    matrizes = [item for item in (manual.get("matrizes") or []) if isinstance(item, dict)]
    local = (meta.get("local") or "Belém-Pará").strip()
    ano = (meta.get("ano") or "2026").strip()

    doc = docx.Document()
    apply_base_styles(doc)
    aplicar_idioma_pt_br(doc)

    sec_capa = _secao_sem_numero(doc, primeira=True, inicio_romano=1)
    aplicar_cabecalho_institucional(sec_capa, meta, assets_dir=assets_dir, space_after=24)
    build_capa(doc, meta, assets_dir=assets_dir)
    aplicar_rodape_local_ano(sec_capa, local, ano)

    sec_rosto = _secao_sem_numero(doc)
    aplicar_cabecalho_institucional(sec_rosto, meta, assets_dir=assets_dir, space_after=18)
    build_folha_rosto(
        doc,
        meta,
        assets_dir=assets_dir,
        texto_natureza=str(secoes.get("texto_folha_rosto") or "").strip() or TEXTO_NATUREZA,
        placeholder_titulo="[TÍTULO DO MANUAL DE CODIFICAÇÃO]",
    )
    aplicar_rodape_local_ano(sec_rosto, local, ano)

    sec_pre = _secao_sem_numero(doc)
    limpar_rodape(sec_pre)
    linhas_limiar = []
    for item in _lista(manual.get("limiares")):
        partes = [parte.strip() for parte in item.split("|")]
        if len(partes) >= 2:
            linhas_limiar.append(partes[:2])
    ilustracoes = _ilustracoes(matrizes)
    if linhas_limiar:
        ilustracoes["tabelas"] = [
            {
                "rotulo": "Tabela",
                "numero": 1,
                "titulo": "Limiares mínimos de aceitação da concordância",
                "bookmark": "cb_tabela_1",
                "origem": "Confiabilidade",
            }
        ]
    if any(ilustracoes.values()):
        build_lista_ilustracoes(doc, ilustracoes, quebrar=False)
    if pares_siglas:
        build_lista_siglas(doc, pares_siglas, quebrar=False, encerrar=not simbolos)
    if simbolos:
        build_lista_simbolos(doc, simbolos, quebrar=bool(pares_siglas))
    build_sumario(doc, dados, quebrar=False)

    textual = doc.add_section(WD_SECTION.CONTINUOUS)
    limpar_rodape(textual)
    _paginar(textual, "decimal", inicio=1)

    adicionar_titulo(doc, "1. IDENTIFICAÇÃO E METADADOS", bookmark="sec_cb_1")
    adicionar_titulo(doc, "1.1 Contexto do projeto", primario=False)
    _corpo(doc, manual.get("contexto"))
    adicionar_titulo(doc, "1.2 Autores e peritos", primario=False)
    _itens(doc, manual.get("autores_peritos"))
    adicionar_titulo(doc, "1.3 Versão corrente e data", primario=False)
    versao = str(manual.get("versao") or "").strip()
    data_versao = str(manual.get("data_versao") or "").strip()
    if versao or data_versao:
        adicionar_paragrafo(doc, f"Versão {versao or '[versão]'}, de {data_versao or '[data]'}.")
    else:
        adicionar_lacuna(doc, "[Informar a versão corrente e a data.]")
    adicionar_titulo(doc, "1.4 Fontes de dados", primario=False)
    _itens(doc, manual.get("fontes_dados"))
    adicionar_titulo(doc, "1.5 Fundamentação teórica e normativa", primario=False)
    _corpo(doc, manual.get("fundamentacao"))

    adicionar_titulo(doc, "2. GOVERNANÇA ÉTICA E SEGURANÇA", bookmark="sec_cb_2")
    adicionar_titulo(doc, "2.1 Desidentificação e anonimização", primario=False)
    _corpo(doc, manual.get("desidentificacao"))
    adicionar_titulo(doc, "2.2 Aprovação em comitês de ética", primario=False)
    _corpo(doc, manual.get("aprovacao_etica"))
    adicionar_titulo(doc, "2.3 Salvaguardas de uso dos dados", primario=False)
    _corpo(doc, manual.get("salvaguardas"))

    adicionar_titulo(doc, "3. REGRAS DE INTERPRETAÇÃO E SEGMENTAÇÃO", bookmark="sec_cb_3")
    adicionar_titulo(doc, "3.1 Polaridade", primario=False)
    _corpo(doc, manual.get("polaridade"))
    adicionar_titulo(doc, "3.2 Sujeito da ação", primario=False)
    _corpo(doc, manual.get("sujeito"))
    adicionar_titulo(doc, "3.3 Temporalidade", primario=False)
    _corpo(doc, manual.get("temporalidade"))
    adicionar_titulo(doc, "3.4 Granularidade sintagmática", primario=False)
    _corpo(doc, manual.get("granularidade"))

    adicionar_titulo(doc, "4. FICHAS TÉCNICAS DAS CATEGORIAS", bookmark="sec_cb_4")
    categorias = [item for item in (manual.get("categorias") or []) if isinstance(item, dict)]
    if not categorias:
        adicionar_lacuna(doc, "[Incluir ao menos uma ficha de categoria.]")
    eixo_anterior = None
    for item in categorias:
        eixo = str(item.get("eixo") or "Sem eixo").strip()
        if eixo != eixo_anterior:
            adicionar_titulo(doc, eixo, primario=False)
            eixo_anterior = eixo
        codigo = str(item.get("codigo") or "").strip()
        nome = str(item.get("nome") or "Categoria").strip()
        rotulo = f"{codigo} {nome}".strip()
        adicionar_titulo(doc, rotulo, primario=False)
        definicao = str(item.get("definicao") or "").strip()
        if definicao:
            adicionar_paragrafo(doc, definicao)
        else:
            adicionar_lacuna(doc, "[Definir a etiqueta.]")
        adicionar_paragrafo(doc, "Critérios de inclusão")
        _itens(doc, item.get("inclusao"))
        adicionar_paragrafo(doc, "Critérios de exclusão")
        _itens(doc, item.get("exclusao"))
        adicionar_paragrafo(doc, "Contraexemplos")
        _itens(doc, item.get("contraexemplos"))

    adicionar_titulo(doc, "5. MATRIZES DE FRONTEIRA E DECISÃO", bookmark="sec_cb_5")
    if not matrizes:
        adicionar_lacuna(doc, "[Incluir um quadro de desempate.]")
    for indice, matriz in enumerate(matrizes, start=1):
        _quadro(
            doc,
            indice,
            str(matriz.get("titulo") or f"Matriz de fronteira {indice}").strip(),
            matriz.get("colunas") or ["Situação limítrofe", "Regra de desempate"],
            matriz.get("linhas") or [],
            str(matriz.get("fonte") or "Construção do(a) autor(a).").strip(),
            f"cb_quadro_{indice}",
        )

    adicionar_titulo(doc, "6. PROTOCOLO DE CONFIABILIDADE E ADJUDICAÇÃO", bookmark="sec_cb_6")
    adicionar_titulo(doc, "6.1 Métricas de concordância", primario=False)
    _corpo(doc, manual.get("metricas"))
    adicionar_titulo(doc, "6.2 Limiares mínimos", primario=False)
    if linhas_limiar:
        inserir_tabela(
            doc,
            1,
            "Limiares mínimos de aceitação da concordância",
            ["Métrica", "Limiar"],
            linhas_limiar,
            "Construção do(a) autor(a).",
            bookmark="cb_tabela_1",
        )
    else:
        _itens(doc, manual.get("limiares"))
        ilustracoes_tabela = None
    adicionar_titulo(doc, "6.3 Fase piloto", primario=False)
    _corpo(doc, manual.get("adjudicacao_piloto"))
    adicionar_titulo(doc, "6.4 Produção", primario=False)
    _corpo(doc, manual.get("adjudicacao_producao"))

    adicionar_titulo(doc, "7. ESPECIFICAÇÃO OPERACIONAL E GOVERNANÇA", bookmark="sec_cb_7")
    adicionar_titulo(doc, "7.1 Interface de coleta", primario=False)
    ferramenta = str(manual.get("ferramenta") or "").strip()
    if ferramenta:
        adicionar_paragrafo(doc, f"Ferramenta de rotulagem: {ferramenta}.")
    configuracao = str(manual.get("configuracao_interface") or "").strip()
    if configuracao:
        p = adicionar_paragrafo(doc, configuracao)
        p.paragraph_format.first_line_indent = Cm(0)
        for run in p.runs:
            run.font.name = "Courier New"
            run.font.size = Pt(9)
    else:
        adicionar_lacuna(doc, "[Colar a configuração XML ou JSON da interface.]")
    adicionar_titulo(doc, "7.2 Histórico de versões", primario=False)
    _itens(doc, manual.get("changelog"))

    renderizar_referencias(doc, _lista(secoes.get("referencias")), titulo="REFERÊNCIAS", bookmark="sec_referencias")

    habilitar_atualizacao_campos(doc)
    doc.save(caminho_saida)
    atualizar_campos_word(caminho_saida)
