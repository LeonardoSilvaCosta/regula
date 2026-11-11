"""Notação com underline vira subscrito no Word (α_ord, κ_w, n_g)."""

import re

# Uma letra ou um grego, depois o sufixo. Siglas (SINT_SONO) não entram.
_SUBSCRITO = re.compile(r"([α-ωΑ-ΩκΔ]|[A-Za-z])_([A-Za-z0-9]+)")


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
        sufixo.font.subscript = True
        pos = ocorrencia.end()
    if not encontrou:
        estilizar(paragrafo.add_run(texto), False)
        return
    if pos < len(texto):
        estilizar(paragrafo.add_run(texto[pos:]), False)
