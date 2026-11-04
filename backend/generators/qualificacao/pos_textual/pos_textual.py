"""
Módulo granular para geração exclusiva da PARTE III (PÓS-TEXTUAL)
conforme o Art. 1º, III da Resolução nº 009/2025-PPGSP/UFPA.
Contempla:
  1. Referências (Obrigatório - ABNT NBR 6023)
  2. Apêndice (Opcional - Produção própria do autor com página dedicada)
  3. Anexo (Opcional - Documentos de terceiros com página dedicada)
"""

from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from core.campos import adicionar_bookmark
from ...common.referencias import (
    adicionar_paragrafo_referencia,
    adicionar_titulo_referencias,
    ordenar_referencias,
)
from ..estrutura import rotulo_pos


def rotulo_e_corpo(item):
    """Devolve (título, corpo). String sem corpo indica entrada só com identificação."""
    if isinstance(item, dict):
        rotulo = str(item.get("titulo") or item.get("rotulo") or "").strip()
        corpo = str(item.get("conteudo") or item.get("corpo") or "").strip()
        return rotulo, corpo
    if isinstance(item, (tuple, list)):
        if len(item) >= 2:
            return str(item[0]).strip(), str(item[1]).strip()
        if item:
            return str(item[0]).strip(), ""
        return "", ""
    if isinstance(item, str):
        texto = item.strip()
        if "\n" in texto:
            primeira, resto = texto.split("\n", 1)
            if resto.strip():
                return primeira.strip(), resto.strip()
        return texto, ""
    return "", ""


def itens_com_corpo(itens):
    """Separa material efetivo de títulos sem conteúdo."""
    validos = []
    omitidos = []
    for item in itens or []:
        rotulo, corpo = rotulo_e_corpo(item)
        if corpo:
            validos.append((rotulo or "Sem título", corpo))
        elif rotulo:
            omitidos.append(rotulo)
    return validos, omitidos


def _escrever_corpo(doc, corpo):
    for paragrafo in str(corpo).split("\n"):
        texto = paragrafo.strip()
        if not texto:
            continue
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Cm(1.27)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(texto)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)


def build_pos_textual(doc, referencias, apendices=None, anexos=None):
    """
    Renderiza os elementos pós-textuais do Relatório de Qualificação.

    Parâmetros:
      - doc: Objeto Document do python-docx
      - referencias: Lista de strings contendo as referências formatadas
      - apendices: Lista de strings/itens com apêndices do autor
      - anexos: Lista de strings/itens com anexos de terceiros
    """

    # -------------------------------------------------------------------------
    # 1. REFERÊNCIAS (Obrigatório - Art. 1º, III, 1)
    # -------------------------------------------------------------------------
    doc.add_page_break()
    adicionar_titulo_referencias(doc, "REFERÊNCIAS", bookmark="sec_referencias")

    if referencias:
        for ref in ordenar_referencias(referencias):
            if str(ref).strip():
                adicionar_paragrafo_referencia(doc, ref)
    else:
        p_aviso = doc.add_paragraph()
        p_aviso.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_aviso.paragraph_format.first_line_indent = Cm(0)
        p_aviso.paragraph_format.line_spacing = 1.5
        r_av = p_aviso.add_run(
            "[ORIENTAÇÃO DE PREENCHIMENTO: Apresente aqui a relação em ordem alfabética de todas as referências "
            "citadas no texto do projeto, em espaçamento simples entre linhas e com espaçamento entre cada referência, "
            "em conformidade com a norma ABNT NBR 6023 e o Art. 1º, III da Resolução nº 009/2025.]"
        )
        r_av.italic = True
        r_av.font.name = "Times New Roman"
        r_av.font.size = Pt(11)
        r_av.font.color.rgb = RGBColor(115, 115, 115)

    _emitir_itens(doc, "APÊNDICE", apendices, "pos_apendice")
    _emitir_itens(doc, "ANEXO", anexos, "pos_anexo")


def _emitir_itens(doc, prefixo, itens, bookmark_prefix):
    if not itens:
        return
    total = len(itens)
    for indice, item in enumerate(itens, start=1):
        doc.add_page_break()
        rotulo, corpo = item if isinstance(item, (tuple, list)) else (str(item), "")
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(18)
        r = p.add_run(rotulo_pos(prefixo, indice, total, rotulo))
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        adicionar_bookmark(p, f"{bookmark_prefix}_{indice}")
        if corpo:
            _escrever_corpo(doc, corpo)