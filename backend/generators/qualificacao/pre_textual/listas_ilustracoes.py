"""
Lista de ilustrações com as sublistas do modelo oficial:
LISTA DE FIGURAS, LISTA DE GRÁFICOS, LISTA DE QUADROS e LISTA DE TABELAS.
"""

from core.campos import adicionar_linha_indice
from ..estrutura import BM_LISTA_ILUSTRACOES, agrupar_ilustracoes
from ..formato import adicionar_subtitulo_lista, adicionar_titulo_lista


def build_lista_ilustracoes(doc, ilustracoes_data, quebrar=False):
    grupos = agrupar_ilustracoes(_extrair_entradas(ilustracoes_data))
    if quebrar:
        doc.add_page_break()
    adicionar_titulo_lista(doc, "LISTA DE ILUSTRAÇÕES", BM_LISTA_ILUSTRACOES)
    for titulo, entradas in grupos:
        adicionar_subtitulo_lista(doc, titulo)
        for rotulo, ref in entradas:
            adicionar_linha_indice(doc, rotulo, ref)
    return [("LISTA DE ILUSTRAÇÕES", BM_LISTA_ILUSTRACOES)]


def _extrair_entradas(ilustracoes_data):
    bruto = ilustracoes_data
    if isinstance(ilustracoes_data, dict):
        bruto = []
        for chave in ("figuras", "graficos", "quadros", "tabelas", "ilustracoes", "lista_quadros", "lista_tabelas"):
            bruto.extend(ilustracoes_data.get(chave) or [])
    entradas = []
    for item in bruto or []:
        if isinstance(item, (tuple, list)) and len(item) >= 2:
            rotulo, ref = item[0], item[1]
            if _parece_bookmark(ref):
                entradas.append((str(rotulo).strip(), str(ref).strip()))
        elif isinstance(item, dict) and item.get("bookmark"):
            entradas.append((str(item.get("titulo", "")).strip(), str(item["bookmark"]).strip()))
    return entradas


def _parece_bookmark(valor):
    texto = str(valor or "").strip()
    if not texto or " " in texto:
        return False
    return texto.startswith("leg_") or texto.startswith("sec_") or texto.startswith("pos_")
