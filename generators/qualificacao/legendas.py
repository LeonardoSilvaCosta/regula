"""Legendas únicas de quadros, tabelas e produtos, usadas no corpo e nas listas."""

LEGENDA_TABELA_1 = (
    "Tabela 1. Distribuição Populacional da Coorte Viva e Alocação Amostral (n = 360)"
)
LEGENDA_TABELA_2 = (
    "Tabela 2. Métricas de Dispersão de Tokens por Prontuário e Limiares de Outliers (Método de Tukey)"
)

BM_QUADRO_1 = "leg_quadro_1"
BM_QUADRO_2 = "leg_quadro_2"
BM_TABELA_1 = "leg_tabela_1"
BM_TABELA_2 = "leg_tabela_2"


def _eh_doutorado(nivel):
    return str(nivel or "").strip().lower() in ("doutorado", "tese")


def legenda_quadro_1(metadata):
    """Mesma frase da apresentação e da lista de quadros."""
    metadata = metadata or {}
    nivel = metadata.get("nivel", "mestrado")
    tipo = "tese" if _eh_doutorado(nivel) else "dissertação"
    titulo = (metadata.get("titulo") or metadata.get("titulo_curto") or "[título da pesquisa]").strip()
    return f"Quadro 1 - Estrutura dos principais itens da {tipo} “{titulo}”."


def legenda_quadro_2(nivel, parte=None):
    """Cronograma. No mestrado há uma única legenda; no doutorado, continua e conclusão."""
    if _eh_doutorado(nivel):
        base = (
            "Quadro 2. Atividades a serem realizadas durante o curso de Doutorado, "
            "no período do mês 1 ao mês 48, no PPGSP da UFPA"
        )
        if parte == "continua":
            return base + " (Continua)."
        if parte == "conclusao":
            return base + " (Conclusão)."
        return base + "."
    return (
        "Quadro 2. Atividades a serem realizadas durante o curso de Mestrado, "
        "no período do mês 1 ao mês 24, no PPGSP da UFPA."
    )


def titulo_produto(indice, ptt, secao=5):
    """Título de subseção: 5.1. PRODUTO 1. Tipo - Título."""
    ptt = ptt or {}
    titulo = str(ptt.get("titulo") or "").strip()
    tipo = str(
        ptt.get("subtipo")
        or ptt.get("subtipo_producao")
        or ptt.get("tipo")
        or ""
    ).strip()
    base = f"{secao}.{indice}. PRODUTO {indice}."
    if tipo and titulo:
        return f"{base} {tipo} - {titulo}"
    if titulo:
        return f"{base} {titulo}"
    if tipo:
        return f"{base} {tipo}"
    return base
