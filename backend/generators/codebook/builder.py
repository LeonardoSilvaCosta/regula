"""Manual de Codificação Operacional e Rotulagem de Prontuários (Codebook)."""
import re
from pathlib import Path

import docx
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

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
from generators.common.pronome import fonte_construcao
from generators.qualificacao.builder import _paginar, _secao_sem_numero, habilitar_atualizacao_campos
from generators.qualificacao.formato import (
    adicionar_lacuna,
    adicionar_paragrafo,
    adicionar_titulo,
    escrever_fonte,
    escrever_legenda,
)
from generators.qualificacao.pre_textual.capa import build_capa
from generators.qualificacao.pre_textual.folha_rosto import build_folha_rosto
from generators.qualificacao.pre_textual.listas_ilustracoes import build_lista_ilustracoes
from generators.qualificacao.pre_textual.listas_siglas import build_lista_siglas, normalizar_siglas
from generators.qualificacao.pre_textual.sumario import build_sumario
from generators.common.siglas_texto import texto_com_sigla
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


def _garantir_ponto(texto):
    texto = str(texto).strip()
    if texto and texto[-1] not in ".!?":
        return f"{texto}."
    return texto


def _corpo_com_ponto(doc, valor):
    paragrafos = [_garantir_ponto(item) for item in _lista(valor)]
    if not paragrafos:
        adicionar_lacuna(doc, "[Preencher]")
        return
    for paragrafo in paragrafos:
        _paragrafo(doc, paragrafo)


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


_RE_VERSAO = re.compile(
    r"^Vers[aã]o\s+([^\s(]+)\s*\(([^)]+)\)\s*:\s*(.+)$",
    re.IGNORECASE,
)


def _registros_versao(valor):
    registros = []
    for item in _lista(valor):
        ocorrencia = _RE_VERSAO.match(item)
        if ocorrencia:
            alteracao = ocorrencia.group(3).strip()
            if alteracao:
                alteracao = alteracao[0].upper() + alteracao[1:]
            registros.append([ocorrencia.group(1), ocorrencia.group(2), alteracao])
        else:
            registros.append(["", "", item])
    return registros


def _quadro(doc, numero, titulo, colunas, linhas, fonte, bookmark, proporcoes=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.0
    escrever_legenda(p, f"Quadro {numero}. {titulo}")
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
    aplicar_autoajuste_janela(tabela, proporcoes)
    for indice, nome in enumerate(colunas):
        _celula(tabela.rows[0].cells[indice], nome, negrito=True)
    for r_idx, linha in enumerate(linhas, start=1):
        for c_idx in range(largura):
            valor = linha[c_idx] if c_idx < len(linha) else ""
            _celula(tabela.rows[r_idx].cells[c_idx], valor)
    _linha_fonte(doc, fonte)


def _sem_rotulo_fonte(texto):
    texto = str(texto or "").strip()
    if texto.lower().startswith("fonte:"):
        return texto.split(":", 1)[1].strip()
    return texto


def _credito_autoral(meta, complemento=""):
    resto = str(complemento or meta.get("ano") or "").strip().rstrip(".")
    return _sem_rotulo_fonte(fonte_construcao(meta, resto))


def _fonte_ilustracao(meta, informado="", complemento=""):
    """Crédito de quadro, tabela ou figura, flexionado pelo pronome quando for de autoria."""
    texto = _sem_rotulo_fonte(informado)
    if texto and not re.match(r"(constru|elaborad)", texto, re.IGNORECASE):
        return texto
    data = str(complemento or "").strip().rstrip(".")
    if not data and "." in texto:
        data = texto.split(".", 1)[1].strip().rstrip(".")
    return _credito_autoral(meta, data)


def _linha_fonte(doc, credito):
    paragrafo = doc.add_paragraph()
    paragrafo.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragrafo.paragraph_format.space_before = Pt(2)
    paragrafo.paragraph_format.space_after = Pt(12)
    paragrafo.paragraph_format.line_spacing = 1.0
    paragrafo.paragraph_format.first_line_indent = Cm(0)
    texto = str(credito or "").strip()
    if not texto.lower().startswith("fonte:"):
        texto = f"Fonte: {texto}" if texto else "Fonte:"
    escrever_fonte(paragrafo, texto)
    return paragrafo


def _run(paragrafo, texto, negrito=False, italico=False):
    run = paragrafo.add_run(texto)
    run.bold = negrito
    run.italic = italico
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    if italico:
        run.font.color.rgb = RGBColor(115, 115, 115)
    return run


def _paragrafo_ficha(doc, antes=8, recuo=0):
    paragrafo = doc.add_paragraph()
    paragrafo.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragrafo.paragraph_format.line_spacing = 1.5
    paragrafo.paragraph_format.space_before = Pt(antes)
    paragrafo.paragraph_format.space_after = Pt(0)
    paragrafo.paragraph_format.left_indent = Cm(recuo)
    paragrafo.paragraph_format.first_line_indent = Cm(0)
    return paragrafo


def _campo(doc, rotulo, texto, pontuar=True):
    paragrafo = _paragrafo_ficha(doc)
    _run(paragrafo, f"{rotulo}: ", negrito=True)
    texto = str(texto or "").strip()
    if not texto:
        _run(paragrafo, "[Preencher]", italico=True)
        return paragrafo
    if pontuar:
        texto = _garantir_ponto(texto)
    _run(paragrafo, texto_com_sigla(doc, texto))
    return paragrafo


def _campo_lista(doc, rotulo, linhas, aspas=False):
    paragrafo = _paragrafo_ficha(doc)
    _run(paragrafo, f"{rotulo}:", negrito=True)
    if not linhas:
        vazio = _paragrafo_ficha(doc, antes=0, recuo=0.75)
        _run(vazio, "[Preencher]", italico=True)
        return
    for linha in linhas:
        texto = _garantir_ponto(linha)
        if aspas and not (texto[:1] in "\"“«" and texto[-1:] in "\"”»"):
            texto = f"“{texto}”"
        item = _paragrafo_ficha(doc, antes=2, recuo=0.75)
        _run(item, texto_com_sigla(doc, texto))


def _sem_prefixo(linha, prefixos):
    baixa = linha.lower()
    for prefixo in prefixos:
        if baixa.startswith(prefixo):
            return linha[len(prefixo) :].strip()
    return None


def _partes_da_ficha(item):
    tipicos = []
    nao_exemplos = []
    decisoes = []
    for linha in _lista(item.get("contraexemplos")):
        tipico = _sem_prefixo(linha, ("exemplo típico:", "exemplo tipico:"))
        nao = _sem_prefixo(linha, ("contraexemplo:", "não-exemplo:", "nao-exemplo:"))
        decisao = _sem_prefixo(linha, ("decisão técnica de fronteira:", "decisao tecnica de fronteira:"))
        if tipico is not None:
            tipicos.append(tipico)
        elif nao is not None:
            nao_exemplos.append(nao)
        elif decisao is not None:
            decisoes.append(decisao[:1].upper() + decisao[1:] if decisao else decisao)
        else:
            tipicos.append(linha)
    return tipicos, nao_exemplos, decisoes


def _ficha(doc, item):
    nome = str(item.get("nome") or "Categoria").strip()
    adicionar_titulo(doc, nome or str(item.get("codigo") or "Categoria").strip(), nivel=3)
    _campo(doc, "Identificador sistêmico", item.get("codigo"), pontuar=False)
    _campo(doc, "Definição breve", item.get("definicao"))
    detalhada = str(item.get("definicao_detalhada") or "").strip()
    if detalhada:
        _campo(doc, "Definição detalhada", detalhada)
    _campo_lista(doc, "Critérios de inclusão", _lista(item.get("inclusao")))
    _campo_lista(doc, "Critérios de exclusão", _lista(item.get("exclusao")))
    tipicos, nao_exemplos, decisoes = _partes_da_ficha(item)
    _campo_lista(doc, "Exemplos típicos", tipicos, aspas=True)
    _campo_lista(doc, "Não-exemplo", nao_exemplos, aspas=True)
    if len(decisoes) <= 1:
        _campo(doc, "Decisão técnica de fronteira", decisoes[0] if decisoes else "")
    else:
        _campo_lista(doc, "Decisão técnica de fronteira", decisoes)


def _preservar_espacos(run):
    texto = run._element.find(qn("w:t"))
    if texto is not None:
        texto.set(qn("xml:space"), "preserve")


def _sombrear_paragrafo(paragrafo):
    p_pr = paragrafo._p.get_or_add_pPr()
    sombreado = OxmlElement("w:shd")
    sombreado.set(qn("w:val"), "clear")
    sombreado.set(qn("w:color"), "auto")
    sombreado.set(qn("w:fill"), "F4F4F4")
    p_pr.append(sombreado)


def _listagem(doc, codigo):
    """Reproduz o código com quebras e indentação, fora do corpo justificado."""
    linhas = str(codigo).replace("\r\n", "\n").replace("\r", "\n").split("\n")
    while linhas and not linhas[-1].strip():
        linhas.pop()
    while linhas and not linhas[0].strip():
        linhas.pop(0)
    if not linhas:
        return
    ultima = len(linhas) - 1
    for indice, linha in enumerate(linhas):
        paragrafo = doc.add_paragraph()
        paragrafo.alignment = WD_ALIGN_PARAGRAPH.LEFT
        paragrafo.paragraph_format.line_spacing = 1.0
        paragrafo.paragraph_format.space_before = Pt(8 if indice == 0 else 0)
        paragrafo.paragraph_format.space_after = Pt(12 if indice == ultima else 0)
        paragrafo.paragraph_format.left_indent = Cm(0.4)
        paragrafo.paragraph_format.right_indent = Cm(0.2)
        paragrafo.paragraph_format.first_line_indent = Cm(0)
        run = paragrafo.add_run(linha if linha else " ")
        run.font.name = "Courier New"
        run.font.size = Pt(8)
        _preservar_espacos(run)
        _sombrear_paragrafo(paragrafo)


def _imagem_interface(assets_dir):
    base = Path(assets_dir)
    if not base.is_absolute():
        base = Path(__file__).resolve().parents[2] / base
    caminho = base / "interface_label_studio.png"
    return caminho if caminho.is_file() else None


def _nivel_sumario(paragrafo, nivel="0"):
    p_pr = paragrafo._p.get_or_add_pPr()
    outline = p_pr.find(qn("w:outlineLvl"))
    if outline is None:
        outline = OxmlElement("w:outlineLvl")
        p_pr.append(outline)
    outline.set(qn("w:val"), nivel)


def _linha_central(doc, texto, antes=0, depois=12, nivel=None, bookmark=None):
    paragrafo = doc.add_paragraph()
    paragrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragrafo.paragraph_format.space_before = Pt(antes)
    paragrafo.paragraph_format.space_after = Pt(depois)
    paragrafo.paragraph_format.line_spacing = 1.5
    paragrafo.paragraph_format.first_line_indent = Cm(0)
    run = paragrafo.add_run(texto)
    run.bold = False
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    if nivel is not None:
        _nivel_sumario(paragrafo, nivel)
    if bookmark:
        adicionar_bookmark(paragrafo, bookmark)
    return paragrafo


def _apendice_interface(doc, configuracao, imagem, fonte):
    doc.add_page_break()
    _linha_central(doc, "APÊNDICE", depois=12, nivel="0", bookmark="sec_apendice")
    _linha_central(
        doc,
        "Apêndice 1: Configuração da interface de coleta",
        antes=0,
        depois=18,
        nivel="1",
    )
    adicionar_paragrafo(
        doc,
        "A especificação a seguir é a configuração carregada na ferramenta de rotulagem. "
        + (
            "A Figura 1 reproduz a tela resultante."
            if imagem is not None
            else "A reprodução da tela fica para uma versão posterior."
        ),
    )
    _listagem(doc, configuracao)
    if imagem is None:
        return
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(12)
    p_img.paragraph_format.space_after = Pt(6)
    p_img.paragraph_format.first_line_indent = Cm(0)
    p_img.add_run().add_picture(str(imagem), width=Cm(16))
    p_leg = doc.add_paragraph()
    p_leg.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_leg.paragraph_format.space_before = Pt(0)
    p_leg.paragraph_format.space_after = Pt(2)
    p_leg.paragraph_format.line_spacing = 1.0
    p_leg.paragraph_format.first_line_indent = Cm(0)
    escrever_legenda(p_leg, "Figura 1. Interface de coleta no Label Studio.")
    adicionar_bookmark(p_leg, "cb_figura_1")
    _linha_fonte(doc, fonte)


def _ilustracoes(matrizes, historico=False, figura=False):
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
    if historico:
        numero = len(quadros) + 1
        quadros.append(
            {
                "rotulo": "Quadro",
                "numero": numero,
                "titulo": "Histórico de versões do manual",
                "bookmark": f"cb_quadro_{numero}",
                "origem": "Governança",
            }
        )
    ilustracoes = {"quadros": quadros, "tabelas": []}
    if figura:
        ilustracoes["figuras"] = [
            {
                "rotulo": "Figura",
                "numero": 1,
                "titulo": "Interface de coleta no Label Studio",
                "bookmark": "cb_figura_1",
                "origem": "Interface de coleta",
            }
        ]
    return ilustracoes


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
    registros_versao = _registros_versao(manual.get("changelog"))
    credito = _credito_autoral(meta, manual.get("data_versao") or meta.get("ano"))
    configuracao_interface = str(manual.get("configuracao_interface") or "").strip()
    imagem_interface = _imagem_interface(assets_dir) if configuracao_interface else None
    ilustracoes = _ilustracoes(
        matrizes,
        historico=bool(registros_versao),
        figura=imagem_interface is not None,
    )
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
        build_lista_ilustracoes(doc, ilustracoes, quebrar=False, titulo_mestre=False)
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
    _corpo_com_ponto(doc, manual.get("fontes_dados"))
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
        _ficha(doc, item)

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
            _fonte_ilustracao(meta, matriz.get("fonte"), manual.get("data_versao") or meta.get("ano")),
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
            credito,
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
        texto_ferramenta = ferramenta.rstrip().rstrip(".")
        adicionar_paragrafo(doc, f"Ferramenta de rotulagem: {texto_ferramenta}.")
    if configuracao_interface:
        adicionar_paragrafo(
            doc,
            "A configuração da interface e a tela de coleta constam no Apêndice 1.",
        )
    else:
        adicionar_lacuna(doc, "[Colar a configuração XML ou JSON da interface.]")
    adicionar_titulo(doc, "7.2 Histórico de versões", primario=False)
    if registros_versao:
        _quadro(
            doc,
            len(matrizes) + 1,
            "Histórico de versões do manual",
            ["Versão", "Data", "Alteração"],
            registros_versao,
            credito,
            f"cb_quadro_{len(matrizes) + 1}",
            proporcoes=[1100, 1500, 6400],
        )
    else:
        adicionar_lacuna(doc, "[Registrar o histórico de versões.]")

    doc.add_page_break()
    renderizar_referencias(doc, _lista(secoes.get("referencias")), titulo="REFERÊNCIAS", bookmark="sec_referencias")
    if configuracao_interface:
        _apendice_interface(
            doc,
            configuracao_interface,
            imagem_interface,
            credito,
        )

    habilitar_atualizacao_campos(doc)
    doc.save(caminho_saida)
    atualizar_campos_word(caminho_saida)
