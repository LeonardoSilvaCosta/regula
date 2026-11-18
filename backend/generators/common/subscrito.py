"""Notação estatística isolada vira subscrito no Word (α_ord, κ_w, n_g)."""

import re

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Só a notação isolada. Identificadores (POLICIAL_HASH, tem_afastamento, SINT_...) ficam intactos.
_SUBSCRITO = re.compile(r"(?<![A-Za-zÀ-ÿ0-9_])([α-ωΑ-Ωκn])_([A-Za-z0-9]+)")


def _marcar_subscrito(run):
    run.font.subscript = True
    r_pr = run._element.get_or_add_rPr()
    vert = r_pr.find(qn("w:vertAlign"))
    if vert is None:
        vert = OxmlElement("w:vertAlign")
        r_pr.append(vert)
    vert.set(qn("w:val"), "subscript")


def escrever_com_subscrito(paragrafo, texto, estilizar):
    """Grava o texto e põe em subscrito o sufixo de notações como α_ord, κ_w e n_g."""
    pos = 0
    encontrou = False
    for ocorrencia in _SUBSCRITO.finditer(texto):
        encontrou = True
        if ocorrencia.start() > pos:
            estilizar(paragrafo.add_run(texto[pos : ocorrencia.start()]), False)
        estilizar(paragrafo.add_run(ocorrencia.group(1)), False)
        sufixo = paragrafo.add_run(ocorrencia.group(2))
        estilizar(sufixo, True)
        _marcar_subscrito(sufixo)
        pos = ocorrencia.end()
    if not encontrou:
        estilizar(paragrafo.add_run(texto), False)
        return
    if pos < len(texto):
        estilizar(paragrafo.add_run(texto[pos:]), False)
