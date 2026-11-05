"""
Resultados preliminares como manuscrito de produto bibliográfico.
"""

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

from ..estrutura import (
    artigo_tem_conteudo,
    artigos_de,
    blocos_manuscrito,
    rotulo_artigo,
)
from ...common.referencias import (
    adicionar_paragrafo_referencia,
    adicionar_titulo_referencias,
    ordenar_referencias,
    titulo_referencias,
)
from ..formato import adicionar_lacuna, adicionar_paragrafo
from ..pre_textual.sumario import registrar_entrada

_TOPICOS_RESUMO = (
    ("Importância do Estudo", ("importancia", "importância", "relevanc")),
    ("Objetivo", ("objetivo",)),
    ("Materiais e Métodos", ("materiais", "metodo", "método")),
    ("Resultados e Discussões", ("resultado", "discuss")),
    ("Conclusões", ("conclus",)),
)

_SUBSECOES_METODO = (
    ("Natureza da Pesquisa", ("natureza",)),
    ("Lócus", ("locus", "lócus", "local")),
    ("Fonte de Dados", ("fonte",)),
    ("Procedimento de Coleta", ("coleta", "procedimento")),
    ("Análise dos Dados", ("analise", "análise")),
)

_NOTAS_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:footnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:footnote w:type="separator" w:id="-1"><w:p><w:r><w:separator/></w:r></w:p></w:footnote>'
    '<w:footnote w:type="continuationSeparator" w:id="0">'
    '<w:p><w:r><w:continuationSeparator/></w:r></w:p></w:footnote>'
    "</w:footnotes>"
)


def build_resultados_preliminares(doc, dados_resultados, numero=7, metadata=None):
    metadata = metadata or {}
    if isinstance(dados_resultados, dict):
        metadata = {**metadata, **(dados_resultados.get("metadata") or {})}
    titulo = _titulo_secao(doc, f"{numero}. RESULTADOS PRELIMINARES", bookmark="sec_resultados")
    registrar_entrada(doc, f"{numero}. RESULTADOS PRELIMINARES", 1, "_TOC_RESULTADOS", titulo)
    artigos = [artigo for artigo in artigos_de(dados_resultados) if artigo_tem_conteudo(artigo)]
    if not artigos:
        adicionar_paragrafo(
            doc,
            "[Seção incompleta para apreciação da banca: não há resultados preliminares informados. "
            "Inclua os resultados já obtidos antes da versão definitiva.]",
        )
        return

    for indice, artigo in enumerate(artigos, start=1):
        p_produto = _titulo_produto(
            doc,
            rotulo_artigo(numero, indice, artigo),
            bookmark=f"sec_res_{indice}",
        )
        _nota_submissao(p_produto, artigo)
        _linha_autoria(doc, artigo, metadata)
        _escrever_manuscrito(doc, artigo, blocos_manuscrito(artigo), capitulo=numero)


def _titulo_secao(doc, texto, bookmark=None):
    from core.campos import ancorar_paragrafo

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(texto.upper())
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    ancorar_paragrafo(p, texto, bookmark=bookmark)
    return p


def _titulo_produto(doc, texto, bookmark=None):
    from core.campos import ancorar_paragrafo

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(texto)
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    if bookmark:
        ancorar_paragrafo(p, texto, bookmark=bookmark)
    return p


def _heading2(doc, texto):
    p = doc.add_paragraph(style="Heading 2")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(texto.upper())
    r.bold = True
    r.italic = False
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    return p


def _subtitulo_metodo(doc, texto):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(texto)
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    return p


def _escrever_manuscrito(doc, artigo, blocos, capitulo=None):
    _resumo(doc, blocos)
    _corpo(doc, "INTRODUÇÃO", blocos.get("introducao"), "Introdução não informada.")
    _heading2(doc, "MATERIAL E MÉTODO")
    subsecoes = _subsecoes_metodo(artigo, blocos.get("metodologia") or "")
    for titulo, texto in subsecoes:
        _subtitulo_metodo(doc, titulo)
        if texto.strip():
            _paragrafos(doc, texto)
        else:
            adicionar_lacuna(doc, f"[{titulo} não informado.]")
    _corpo(
        doc,
        "RESULTADOS E DISCUSSÕES",
        blocos.get("resultados"),
        "Resultados e discussões não informados.",
    )
    _corpo(
        doc,
        "CONSIDERAÇÕES FINAIS",
        _consideracoes(artigo, blocos),
        "Considerações finais não informadas.",
    )
    _referencias(doc, blocos.get("referencias"), capitulo=capitulo)


def _resumo(doc, blocos):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run("Resumo")
    r.bold = True
    r.italic = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    encontrados = _mapear_topicos(blocos.get("topicos") or [])
    if encontrados:
        for rotulo, _chaves in _TOPICOS_RESUMO:
            _rotulo_e_texto(doc, rotulo, encontrados.get(rotulo) or "[não informado]")
    elif blocos.get("resumo"):
        _paragrafo_simples(doc, blocos["resumo"])
    else:
        for rotulo, _chaves in _TOPICOS_RESUMO:
            _rotulo_e_texto(doc, rotulo, "[não informado]")
    _rotulo_e_texto(doc, "Palavras-chave", blocos.get("palavras_chave") or "[3 a 5 palavras separadas por ponto e vírgula]")


def _mapear_topicos(topicos):
    pares = []
    for item in topicos:
        if isinstance(item, (tuple, list)) and len(item) >= 2:
            pares.append((str(item[0]), str(item[1])))
        elif isinstance(item, dict):
            pares.append((str(item.get("rotulo") or item.get("titulo") or ""), str(item.get("texto") or "")))
    achados = {}
    for rotulo, chaves in _TOPICOS_RESUMO:
        for nome, texto in pares:
            baixo = _sem_acento(nome)
            if any(chave in baixo for chave in chaves):
                achados[rotulo] = texto
                break
    return achados


def _subsecoes_metodo(artigo, metodologia):
    chaves = {
        "Natureza da Pesquisa": ("natureza_pesquisa", "natureza", "metodologia_natureza"),
        "Lócus": ("locus", "lócus", "metodologia_locus"),
        "Fonte de Dados": ("fonte_dados", "fontes", "metodologia_fontes"),
        "Procedimento de Coleta": ("procedimento_coleta", "coleta", "metodologia_coleta"),
        "Análise dos Dados": ("analise_dados", "analise", "metodologia_analise"),
    }
    textos = {}
    for titulo, nomes in chaves.items():
        for nome in nomes:
            valor = str(artigo.get(nome) or "").strip()
            if valor:
                textos[titulo] = valor
                break
    if not any(textos.values()) and metodologia.strip():
        partes = _fatiar_subsecoes(metodologia)
        if partes:
            textos.update(partes)
        else:
            textos["Natureza da Pesquisa"] = metodologia.strip()
    return [(titulo, textos.get(titulo, "")) for titulo, _chaves in _SUBSECOES_METODO]


def _fatiar_subsecoes(texto):
    import re

    marcas = [(titulo, chaves) for titulo, chaves in _SUBSECOES_METODO]
    linhas = texto.splitlines()
    atual = None
    blocos = {}
    for linha in linhas:
        baixo = _sem_acento(linha.strip().rstrip(":"))
        destino = None
        for titulo, chaves in marcas:
            if any(baixo.startswith(chave) for chave in chaves):
                destino = titulo
                break
        if destino:
            atual = destino
            resto = re.sub(r"^[^:]+:\s*", "", linha.strip())
            if resto and _sem_acento(resto) != baixo:
                blocos.setdefault(atual, []).append(resto)
            continue
        if atual:
            blocos.setdefault(atual, []).append(linha)
    return {titulo: "\n".join(partes).strip() for titulo, partes in blocos.items()}


def _consideracoes(artigo, blocos):
    for chave in ("consideracoes_finais", "consideracoes", "conclusao"):
        valor = str(artigo.get(chave) or "").strip()
        if valor:
            return valor
    for titulo, texto in blocos.get("extras") or []:
        baixo = _sem_acento(titulo)
        if "considerac" in baixo or "conclus" in baixo:
            return texto
    return ""


def _corpo(doc, titulo, texto, aviso):
    _heading2(doc, titulo)
    if str(texto or "").strip():
        _paragrafos(doc, texto)
    else:
        adicionar_lacuna(doc, f"[{aviso}]")


def _paragrafos(doc, texto):
    for parte in str(texto).split("\n"):
        if parte.strip():
            adicionar_paragrafo(doc, parte.strip())


def _referencias(doc, texto, capitulo=None):
    adicionar_titulo_referencias(doc, titulo_referencias(capitulo))
    linhas = [linha.strip() for linha in str(texto or "").split("\n") if linha.strip()]
    if not linhas:
        adicionar_lacuna(doc, "[Referências do manuscrito não informadas.]")
        return
    for linha in ordenar_referencias(linhas):
        adicionar_paragrafo_referencia(doc, linha)


def _rotulo_e_texto(doc, rotulo, texto):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    r1 = p.add_run(f"{rotulo}: ")
    r1.bold = True
    r1.italic = False
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(12)
    r2 = p.add_run(str(texto))
    r2.bold = False
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(12)


def _paragrafo_simples(doc, texto):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(str(texto))
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)


def _linha_autoria(doc, artigo, metadata):
    discente = _primeiro(
        artigo.get("discente"),
        artigo.get("autor"),
        metadata.get("autor"),
        (_listar_autores(artigo) or [""])[0],
    )
    orientador = _primeiro(artigo.get("orientador"), metadata.get("orientador"))
    coorientador = _primeiro(artigo.get("coorientador"), metadata.get("coorientador"))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    papeis = (
        (discente, "Discente (1º autor)"),
        (orientador, "Orientador"),
        (coorientador, "Coorientador"),
    )
    escritos = [(nome, papel) for nome, papel in papeis if nome]
    if not escritos:
        r = p.add_run("[Autoria não informada.]")
        r.italic = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        return
    for indice, (nome, papel) in enumerate(escritos):
        if indice:
            sep = p.add_run("; ")
            sep.font.name = "Times New Roman"
            sep.font.size = Pt(12)
        r_nome = p.add_run(nome)
        r_nome.bold = True
        r_nome.font.name = "Times New Roman"
        r_nome.font.size = Pt(12)
        r_papel = p.add_run(f" ({papel})")
        r_papel.italic = True
        r_papel.font.name = "Times New Roman"
        r_papel.font.size = Pt(12)


def _nota_submissao(paragrafo, artigo):
    revista = _primeiro(artigo.get("revista_pretendida"), artigo.get("revista")) or "[revista não informada]"
    qualis = _primeiro(artigo.get("qualis_capes"), artigo.get("qualis")) or "[Qualis não informado]"
    status = _primeiro(artigo.get("status"), artigo.get("status_submissao")) or "[status não informado]"
    texto = (
        f"Artigo elaborado para submissão à revista {revista} (Qualis {qualis}). Status: {status}."
    )
    _adicionar_nota(paragrafo, texto)


def _adicionar_nota(paragrafo, texto):
    parte = _parte_notas(paragrafo.part)
    raiz = parte.element
    proximo = 1
    for nota in raiz.findall(qn("w:footnote")):
        bruto = nota.get(qn("w:id"))
        if bruto and bruto.lstrip("-").isdigit():
            proximo = max(proximo, int(bruto) + 1)
    nota = OxmlElement("w:footnote")
    nota.set(qn("w:id"), str(proximo))
    p = OxmlElement("w:p")
    r = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    fontes = OxmlElement("w:rFonts")
    fontes.set(qn("w:ascii"), "Times New Roman")
    fontes.set(qn("w:hAnsi"), "Times New Roman")
    tamanho = OxmlElement("w:sz")
    tamanho.set(qn("w:val"), "20")
    r_pr.append(fontes)
    r_pr.append(tamanho)
    r.append(r_pr)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = texto
    r.append(t)
    p.append(r)
    nota.append(p)
    raiz.append(nota)

    run = paragrafo.add_run()
    run.font.superscript = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    ref = OxmlElement("w:footnoteReference")
    ref.set(qn("w:id"), str(proximo))
    run._r.append(ref)


def _parte_notas(parte_documento):
    try:
        return parte_documento.part_related_by(RT.FOOTNOTES)
    except KeyError:
        from docx.opc.packuri import PackURI
        from docx.opc.part import XmlPart

        parte = XmlPart.load(
            PackURI("/word/footnotes.xml"),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml",
            _NOTAS_XML.encode("utf-8"),
            parte_documento.package,
        )
        parte_documento.relate_to(parte, RT.FOOTNOTES)
        return parte


def _listar_autores(artigo):
    bruto = artigo.get("autores_lista", artigo.get("autores"))
    if not bruto:
        return []
    if isinstance(bruto, str):
        partes = [p.strip() for p in bruto.replace(";", "\n").split("\n")]
    else:
        partes = [str(p).strip() for p in bruto]
    return [p for p in partes if p and not p.lower().startswith("autor ")]


def _primeiro(*valores):
    for valor in valores:
        texto = str(valor or "").strip()
        if texto:
            return texto
    return ""


def _sem_acento(texto):
    import unicodedata

    normal = unicodedata.normalize("NFD", texto or "")
    return "".join(c for c in normal if unicodedata.category(c) != "Mn").lower()
