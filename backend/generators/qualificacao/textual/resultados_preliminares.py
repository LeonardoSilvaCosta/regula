"""
Resultados preliminares como manuscrito de produto bibliográfico.
"""

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

from ..estrutura import (
    artigo_tem_conteudo,
    artigos_de,
    blocos_manuscrito,
    rotulo_artigo,
)
from ..formato import adicionar_lacuna, adicionar_paragrafo, adicionar_titulo


def build_resultados_preliminares(doc, dados_resultados, numero=7):
    adicionar_titulo(doc, f"{numero}. RESULTADOS PRELIMINARES", bookmark="sec_resultados")
    artigos = [artigo for artigo in artigos_de(dados_resultados) if artigo_tem_conteudo(artigo)]
    if not artigos:
        adicionar_paragrafo(
            doc,
            "[Seção incompleta para apreciação da banca: não há resultados preliminares informados. "
            "Inclua os resultados já obtidos antes da versão definitiva.]",
        )
        return

    adicionar_paragrafo(
        doc,
        "Em cumprimento ao Art. 1º, II, item 3 da Resolução nº 009/2025-PPGSP/UFPA, "
        "apresenta-se o estágio dos produtos bibliográficos para apreciação da banca examinadora.",
    )

    for indice, artigo in enumerate(artigos, start=1):
        adicionar_titulo(
            doc,
            rotulo_artigo(numero, indice, artigo),
            bookmark=f"sec_res_{indice}",
            primario=False,
        )
        for autor in _listar_autores(artigo):
            p_aut = doc.add_paragraph()
            p_aut.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            p_aut.paragraph_format.line_spacing = 1.0
            p_aut.paragraph_format.space_before = Pt(0)
            p_aut.paragraph_format.space_after = Pt(2)
            r_a = p_aut.add_run(autor)
            r_a.font.name = "Times New Roman"
            r_a.font.size = Pt(12)
        _escrever_manuscrito(doc, blocos_manuscrito(artigo))


def _escrever_manuscrito(doc, blocos):
    adicionar_titulo(doc, "RESUMO", primario=False, marcar=False)
    if blocos.get("topicos") or blocos.get("palavras_chave"):
        for item in blocos.get("topicos") or []:
            if isinstance(item, (tuple, list)) and len(item) >= 2:
                rotulo, texto = item[0], item[1]
            elif isinstance(item, dict):
                rotulo = item.get("rotulo") or item.get("titulo") or ""
                texto = item.get("texto") or ""
            else:
                continue
            _rotulo_e_texto(doc, rotulo, texto)
        if blocos.get("palavras_chave"):
            _rotulo_e_texto(doc, "Palavras-chave", blocos["palavras_chave"])
    elif blocos.get("resumo"):
        adicionar_paragrafo(doc, blocos["resumo"])
    else:
        adicionar_lacuna(doc, "[Resumo não informado.]")

    _bloco(doc, "INTRODUÇÃO", blocos.get("introducao"), "Introdução não informada.")
    _bloco(doc, "METODOLOGIA", blocos.get("metodologia"), "Metodologia não informada.")
    _bloco(doc, "RESULTADOS PARCIAIS", blocos.get("resultados"), "Resultados parciais não informados.")
    _referencias(doc, blocos.get("referencias"))

    for titulo, texto in blocos.get("extras") or []:
        adicionar_titulo(doc, titulo, primario=False, marcar=False)
        adicionar_paragrafo(doc, texto)


def _bloco(doc, titulo, texto, aviso):
    adicionar_titulo(doc, titulo, primario=False, marcar=False)
    if str(texto or "").strip():
        for parte in str(texto).split("\n"):
            if parte.strip():
                adicionar_paragrafo(doc, parte.strip())
    else:
        adicionar_lacuna(doc, f"[{aviso}]")


def _referencias(doc, texto):
    adicionar_titulo(doc, "REFERÊNCIAS", primario=False, marcar=False)
    linhas = [linha.strip() for linha in str(texto or "").split("\n") if linha.strip()]
    if not linhas:
        adicionar_lacuna(doc, "[Referências do manuscrito não informadas.]")
        return
    for linha in linhas:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(12)
        r = p.add_run(linha)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)


def _rotulo_e_texto(doc, rotulo, texto):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    r1 = p.add_run(f"{rotulo}: ")
    r1.bold = True
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(12)
    r2 = p.add_run(str(texto))
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(12)


def _listar_autores(artigo):
    bruto = artigo.get("autores_lista", artigo.get("autores"))
    if not bruto:
        return []
    if isinstance(bruto, str):
        partes = [p.strip() for p in bruto.replace(";", "\n").split("\n")]
    else:
        partes = [str(p).strip() for p in bruto]
    return [p for p in partes if p and not p.lower().startswith("autor ")]
