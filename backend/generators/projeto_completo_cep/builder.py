"""Projeto Completo CEP com capa, folha de rosto e corpo no padrão da qualificação."""
import re

import docx
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

from core.atualizar_campos import atualizar_campos_word
from core.styles import (
    apply_base_styles,
    aplicar_cabecalho_institucional,
    aplicar_idioma_pt_br,
    aplicar_rodape_local_ano,
    limpar_rodape,
)
from core.xml_utils import aplicar_autoajuste_janela, set_cell_border
from generators.common.referencias import renderizar_referencias
from generators.qualificacao.builder import (
    _paginar,
    _secao_sem_numero,
    habilitar_atualizacao_campos,
)
from generators.qualificacao.formato import (
    adicionar_lacuna,
    adicionar_paragrafo,
    adicionar_titulo,
    escrever_fonte,
    escrever_legenda,
)
from generators.qualificacao.pre_textual.capa import build_capa
from generators.qualificacao.pre_textual.folha_rosto import build_folha_rosto
from generators.qualificacao.pre_textual.listas_siglas import build_lista_siglas, normalizar_siglas
from generators.qualificacao.pre_textual.sumario import build_sumario
from generators.qualificacao.textual.cronograma import build_cronograma

TEXTO_NATUREZA = (
    "Projeto Detalhado de Pesquisa apresentado ao Comitê de Ética em Pesquisa do Instituto de "
    "Ciências da Saúde da Universidade Federal do Pará (CEP/ICS/UFPA) e ao Colegiado do Programa "
    "de Pós-Graduação em Segurança Pública (PPGSP/ICEN/UFPA), vinculado ao desenvolvimento da "
    "Dissertação de Mestrado Profissional em Segurança Pública."
)
_RE_SUBTITULO = re.compile(r"^\d+\.\d+(?:\.\d+)?\.?\s+\S")
_RE_STATUS = re.compile(r"\s*Status:\s*", re.IGNORECASE)
_RE_SEPARADOR = re.compile(r"\s+[—–-]\s+")
_RE_ITEM = re.compile(r"^\s*[\*\-•]\s*")
_RE_VALOR = re.compile(r"R\$\s*[\d\.]+,\d{2}")
_RE_CLASSE = re.compile(r"\((Capital|Custeio)\)", re.IGNORECASE)


def _lista(valor):
    if valor is None:
        return []
    if isinstance(valor, (list, tuple)):
        return [str(item).strip() for item in valor if str(item).strip()]
    texto = str(valor).strip()
    return [texto] if texto else []


def _titulo_centralizado(doc, texto):
    p = doc.add_paragraph(style="Heading 1")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(18)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(texto)
    r.bold = False
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    return p


def _celula(celula, texto, negrito=False, centro=False):
    celula.text = texto
    celula.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = celula.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if centro else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    if p.runs:
        p.runs[0].font.name = "Times New Roman"
        p.runs[0].font.size = Pt(10)
        p.runs[0].bold = negrito
    set_cell_border(celula, top={"sz": 4}, bottom={"sz": 4}, left={"sz": 4}, right={"sz": 4})


def _quadro(doc, numero, titulo, colunas, linhas, proporcoes, ano):
    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_tit.paragraph_format.space_before = Pt(18)
    p_tit.paragraph_format.space_after = Pt(4)
    p_tit.paragraph_format.line_spacing = 1.0
    escrever_legenda(p_tit, f"Quadro {numero}. {titulo}", tamanho=12)

    tabela = doc.add_table(rows=1 + len(linhas), cols=len(colunas))
    tabela.alignment = WD_TABLE_ALIGNMENT.LEFT
    aplicar_autoajuste_janela(tabela, proporcoes)
    for idx, nome in enumerate(colunas):
        _celula(tabela.rows[0].cells[idx], nome, negrito=True, centro=True)
    for r_idx, linha in enumerate(linhas, start=1):
        for c_idx, valor in enumerate(linha):
            _celula(tabela.rows[r_idx].cells[c_idx], valor, centro=c_idx > 0)

    p_fonte = doc.add_paragraph()
    p_fonte.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_fonte.paragraph_format.space_before = Pt(2)
    p_fonte.paragraph_format.space_after = Pt(18)
    p_fonte.paragraph_format.line_spacing = 1.0
    escrever_fonte(p_fonte, f"Fonte: Elaborado pelo(a) autor(a), {ano}.")


def _linha_cronograma(texto):
    status = ""
    corpo = texto
    partes_status = _RE_STATUS.split(texto, maxsplit=1)
    if len(partes_status) == 2:
        corpo, status = partes_status[0].strip().rstrip("."), partes_status[1].strip().rstrip(".")
    partes = _RE_SEPARADOR.split(corpo, maxsplit=1)
    if len(partes) == 2:
        return [partes[0].strip(), partes[1].strip(), status]
    return [corpo.strip(), "", status]


def _quadro_cronograma(doc, paragrafos, ano):
    linhas = [_linha_cronograma(item) for item in paragrafos]
    _quadro(
        doc,
        1,
        "Cronograma de execução da pesquisa.",
        ["Período", "Atividade", "Status"],
        linhas,
        [1800, 6200, 1400],
        ano,
    )


def _itens_orcamento(paragrafos):
    intro = []
    itens = []
    for paragrafo in paragrafos:
        for trecho in str(paragrafo).splitlines():
            trecho = trecho.strip()
            if not trecho:
                continue
            if _RE_ITEM.match(trecho) or _RE_CLASSE.search(trecho) or trecho.lower().startswith("total"):
                bruto = _RE_ITEM.sub("", trecho).strip()
                classe = ""
                achado = _RE_CLASSE.search(bruto)
                if achado:
                    classe = achado.group(1).capitalize()
                    bruto = (bruto[: achado.start()] + bruto[achado.end() :]).strip(" :")
                valor = ""
                achado_valor = _RE_VALOR.search(bruto)
                if achado_valor:
                    valor = achado_valor.group(0)
                    bruto = (bruto[: achado_valor.start()] + bruto[achado_valor.end() :]).strip(" :")
                itens.append([bruto, valor, classe])
            else:
                intro.append(trecho)
    return intro, itens


def _quadro_orcamento(doc, paragrafos, ano):
    intro, itens = _itens_orcamento(paragrafos)
    for paragrafo in intro:
        if not paragrafo.lower().startswith("total"):
            adicionar_paragrafo(doc, paragrafo)
    if not itens:
        _corpo(doc, paragrafos)
        return
    _quadro(
        doc,
        2,
        "Orçamento da pesquisa.",
        ["Item", "Valor", "Natureza"],
        itens,
        [6200, 1800, 1400],
        ano,
    )


def _limite_sigla(sigla):
    return (
        r"(?<![A-Za-zÀ-ÿ0-9/])"
        + re.escape(sigla)
        + r"(?![A-Za-zÀ-ÿ0-9/])"
    )


def _ocorrencias(texto, sigla, significado, inicio):
    """Forma expandida, sigla isolada e nome por extenso, a partir de `inicio`."""
    expandidos = list(
        re.finditer(
            re.escape(significado) + r"\s*\(\s*" + re.escape(sigla) + r"\s*\)",
            texto[inicio:],
            flags=re.IGNORECASE,
        )
    )
    siglas = list(re.finditer(_limite_sigla(sigla), texto[inicio:]))
    nomes = list(
        re.finditer(
            r"(?<![A-Za-zÀ-ÿ])" + re.escape(significado) + r"(?![A-Za-zÀ-ÿ])",
            texto[inicio:],
            flags=re.IGNORECASE,
        )
    )
    achados = []
    for match in expandidos:
        achados.append((inicio + match.start(), inicio + match.end(), "expandida", match.group(0)))
    for match in siglas:
        achados.append((inicio + match.start(), inicio + match.end(), "sigla", match.group(0)))
    for match in nomes:
        achados.append((inicio + match.start(), inicio + match.end(), "nome", match.group(0)))
    return achados


def _normalizar_siglas_texto(texto, pares, introduzidas):
    if not texto or not pares:
        return texto
    ordenados = sorted(pares, key=lambda par: len(par[1]), reverse=True)
    cursor = 0
    partes = []
    while cursor < len(texto):
        escolhido = None
        for sigla, significado in ordenados:
            if not significado:
                continue
            for inicio, fim, tipo, trecho in _ocorrencias(texto, sigla, significado, cursor):
                if escolhido is None or inicio < escolhido[0] or (
                    inicio == escolhido[0] and fim - inicio > escolhido[1] - escolhido[0]
                ):
                    escolhido = (inicio, fim, tipo, trecho, sigla, significado)
        if escolhido is None:
            partes.append(texto[cursor:])
            break
        inicio, fim, tipo, trecho, sigla, significado = escolhido
        chave = sigla.upper()
        ja_introduzida = bool(introduzidas.get(chave))
        parentese = re.match(r"\s*\(([^)]*)\)", texto[fim:])
        sigla_no_parentese = bool(
            parentese
            and re.search(
                r"(?<![A-Za-zÀ-ÿ0-9])" + re.escape(sigla) + r"(?![A-Za-zÀ-ÿ0-9])",
                parentese.group(1),
            )
        )
        if tipo == "nome" and sigla_no_parentese:
            fim += parentese.end()
            tipo = "expandida"
            trecho = texto[inicio:fim]
        partes.append(texto[cursor:inicio])
        composto = parentese.group(1).strip() if parentese and "/" in parentese.group(1) else ""
        if tipo == "expandida" and ja_introduzida:
            partes.append(composto or sigla)
        elif tipo == "expandida":
            partes.append(trecho)
        elif tipo == "sigla" and not ja_introduzida:
            partes.append(f"{significado} ({sigla})")
        elif tipo == "sigla":
            partes.append(trecho)
        elif not ja_introduzida:
            partes.append(f"{trecho} ({sigla})")
        else:
            partes.append(sigla)
        introduzidas[chave] = True
        cursor = fim
    return "".join(partes)


def _aplicar_siglas(secoes, pares):
    if not pares:
        return secoes
    introduzidas = {sigla.upper(): False for sigla, _ in pares}
    saida = dict(secoes)

    def converter(valor):
        if isinstance(valor, str):
            return _normalizar_siglas_texto(valor, pares, introduzidas)
        if isinstance(valor, (list, tuple)):
            return [converter(item) for item in valor]
        return valor

    chaves = [
        "introducao",
        "problema",
        "justificativa",
        "hipotese",
        "objetivo_geral",
        "objetivos_especificos",
    ]
    if _lista(saida.get("referencial_teorico")):
        chaves.append("referencial_teorico")
    else:
        chaves.append("revisao")
    chaves.extend(
        [
            "metodologia_natureza",
            "metodologia_participantes",
            "metodologia_locus",
            "metodologia_fontes",
            "metodologia_criterios",
            "metodologia_coleta",
            "metodologia_analise",
        ]
    )
    if _lista(saida.get("aspectos_eticos")):
        chaves.append("aspectos_eticos")
    else:
        chaves.extend(["riscos", "beneficios", "lgpd_governanca", "metodologia_etica"])
    chaves.extend(["cronograma_texto", "orcamento"])
    for chave in chaves:
        if chave in saida:
            saida[chave] = converter(saida.get(chave))
    return saida


def _corpo(doc, valor, recuo=True):
    paragrafos = _lista(valor)
    if not paragrafos:
        adicionar_lacuna(doc, "[Preencher]")
        return
    for paragrafo in paragrafos:
        if _RE_SUBTITULO.match(paragrafo):
            adicionar_titulo(doc, paragrafo, primario=False)
        else:
            p = adicionar_paragrafo(doc, paragrafo)
            if not recuo:
                p.paragraph_format.first_line_indent = Cm(0)


def gerar_documento_projeto_completo_cep(
    caminho_saida,
    revisao=None,
    nivel="mestrado",
    assets_dir="assets",
):
    dados = revisao or {}
    meta = dict(dados.get("metadata") or {})
    meta["nivel"] = str(nivel or meta.get("nivel") or "mestrado").strip().lower()
    pares_siglas = normalizar_siglas(dados.get("siglas") or meta.get("siglas"))
    secoes = _aplicar_siglas(dict(dados.get("sections") or {}), pares_siglas)
    local = (meta.get("local") or "Belém-Pará").strip()
    ano = (meta.get("ano") or "2026").strip()

    doc = docx.Document()
    apply_base_styles(doc)

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
        placeholder_titulo="[TÍTULO DO PROJETO DE PESQUISA]",
        complemento=_lista(secoes.get("compromisso_etico")),
    )
    aplicar_rodape_local_ano(sec_rosto, local, ano)

    sec_pre = _secao_sem_numero(doc)
    limpar_rodape(sec_pre)
    if pares_siglas:
        build_lista_siglas(doc, pares_siglas, quebrar=False, encerrar=True)
    build_sumario(doc, dados, quebrar=False)

    # O sumário já fecha com quebra de página; a seção contínua evita página em branco.
    textual = doc.add_section(WD_SECTION.CONTINUOUS)
    limpar_rodape(textual)
    _paginar(textual, "decimal", inicio=1)

    if _lista(secoes.get("resumo")) or str(secoes.get("palavras_chave") or "").strip():
        _titulo_centralizado(doc, "RESUMO")
        _corpo(doc, secoes.get("resumo"), recuo=False)
        palavras = str(secoes.get("palavras_chave") or "").strip()
        if palavras:
            p_chaves = adicionar_paragrafo(doc, f"Palavras-chave: {palavras}")
            p_chaves.paragraph_format.first_line_indent = Cm(0)

    adicionar_titulo(doc, "1. INTRODUÇÃO")
    adicionar_titulo(doc, "1.1 Contextualização", primario=False)
    _corpo(doc, secoes.get("introducao"))
    adicionar_titulo(doc, "1.2 Problema de pesquisa", primario=False)
    _corpo(doc, secoes.get("problema"))

    adicionar_titulo(doc, "2. JUSTIFICATIVA")
    _corpo(doc, secoes.get("justificativa"))

    adicionar_titulo(doc, "3. HIPÓTESE E OBJETIVOS")
    adicionar_titulo(doc, "3.1 Hipótese", primario=False)
    _corpo(doc, secoes.get("hipotese"))
    adicionar_titulo(doc, "3.2 Objetivo geral", primario=False)
    geral = str(secoes.get("objetivo_geral") or "").strip()
    if geral:
        adicionar_paragrafo(doc, geral)
    else:
        adicionar_lacuna(doc, "[Preencher]")
    adicionar_titulo(doc, "3.3 Objetivos específicos", primario=False)
    _corpo(doc, secoes.get("objetivos_especificos"))

    adicionar_titulo(doc, "4. REFERENCIAL TEÓRICO")
    referencial = _lista(secoes.get("referencial_teorico")) or _lista(secoes.get("revisao"))
    _corpo(doc, referencial)

    adicionar_titulo(doc, "5. METODOLOGIA")
    natureza = _lista(secoes.get("metodologia_natureza"))
    metodologia_partida = any(
        _lista(secoes.get(chave))
        for chave in ("metodologia_participantes", "metodologia_fontes", "metodologia_criterios", "metodologia_coleta")
    ) or str(secoes.get("metodologia_locus") or "").strip()
    if natureza and not metodologia_partida:
        _corpo(doc, natureza)
    else:
        adicionar_titulo(doc, "5.1 Delineamento", primario=False)
        _corpo(doc, natureza)
        adicionar_titulo(doc, "5.2 População", primario=False)
        _corpo(doc, secoes.get("metodologia_participantes"))
        adicionar_titulo(doc, "5.3 Dados", primario=False)
        fontes = _lista(secoes.get("metodologia_fontes"))
        locus = str(secoes.get("metodologia_locus") or "").strip()
        if locus:
            fontes = [f"Lócus: {locus}"] + fontes
        _corpo(doc, fontes)
        adicionar_titulo(doc, "5.4 Critérios", primario=False)
        _corpo(doc, secoes.get("metodologia_criterios"))
        adicionar_titulo(doc, "5.5 Procedimentos", primario=False)
        _corpo(doc, secoes.get("metodologia_coleta"))

    adicionar_titulo(doc, "6. ANÁLISE DOS DADOS")
    _corpo(doc, secoes.get("metodologia_analise"))

    adicionar_titulo(doc, "7. ASPECTOS ÉTICOS")
    aspectos = _lista(secoes.get("aspectos_eticos"))
    if aspectos:
        _corpo(doc, aspectos)
    else:
        adicionar_titulo(doc, "7.1 Riscos", primario=False)
        _corpo(doc, secoes.get("riscos"))
        adicionar_titulo(doc, "7.2 Benefícios", primario=False)
        _corpo(doc, secoes.get("beneficios"))
        adicionar_titulo(doc, "7.3 Sigilo, LGPD e governança", primario=False)
        etica = _lista(secoes.get("lgpd_governanca")) or _lista(secoes.get("metodologia_etica"))
        _corpo(doc, etica)

    cronograma_texto = _lista(secoes.get("cronograma_texto"))
    if cronograma_texto:
        adicionar_titulo(doc, "8. CRONOGRAMA")
        _quadro_cronograma(doc, cronograma_texto, ano)
    else:
        projeto = {
            "cronograma": dados.get("cronograma") or [],
            "ano": ano,
        }
        build_cronograma(doc, projeto, nivel=meta["nivel"], ano_referencia=ano, numero=8)

    adicionar_titulo(doc, "9. ORÇAMENTO")
    orcamento = _lista(secoes.get("orcamento"))
    if orcamento:
        _quadro_orcamento(doc, orcamento, ano)
    else:
        adicionar_lacuna(doc, "[Preencher]")

    renderizar_referencias(doc, _lista(secoes.get("referencias")))
    aplicar_idioma_pt_br(doc)
    habilitar_atualizacao_campos(doc)
    doc.save(caminho_saida)
    atualizar_campos_word(caminho_saida)
    return caminho_saida
