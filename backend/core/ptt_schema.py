"""Validador e schema estruturado dos 22 itens obrigatórios da Resolução nº 007/2025-PPGSP."""

def validar_carteira_produtos(ptts, min_produtos=4):
    """
    Valida as proporções da carteira de produtos segundo a Resolução 007/2025:
    - Mínimo de produtos (4 para mestrado, 8 para doutorado)
    - Máximo de 25% Baixa
    - Máximo de 25% Média
    - Mínimo de 50% Alta
    """
    total = len(ptts)
    if total < min_produtos:
        return False, f"Quantidade insuficiente de PTTs: {total} (Mínimo exigido: {min_produtos})"

    impacto_alto = sum(1 for p in ptts if p.get('impacto', '').lower() == 'alto')
    prop_alta = impacto_alto / total

    if prop_alta < 0.50:
        return False, f"Proporção de produtos de impacto Alto é de {prop_alta*100:.1f}% (Mínimo exigido: 50%)"

    return True, "Carteira de produtos em conformidade com a Resolução 007/2025."

_AREA = "Segurança Pública, Justiça, Conflitos e Cidadania"
_LINHA = "Políticas, Gestão, Direitos Humanos, Criminalidade e Tecnologia da Informação"


def _valor(dados_ptt, *chaves):
    for chave in chaves:
        texto = str((dados_ptt or {}).get(chave) or "").strip()
        if texto:
            return texto
    return ""


def _contexto(dados_projeto):
    dados_projeto = dados_projeto or {}
    return {
        "autoria": _valor(dados_projeto, "autor", "autoria"),
        "ano": _valor(dados_projeto, "ano"),
        "area": _valor(dados_projeto, "area_concentracao") or _AREA,
        "linha": _valor(dados_projeto, "linha_pesquisa") or _LINHA,
        "projeto": _valor(dados_projeto, "titulo", "projeto_pesquisa"),
        "coautoria": _coautoria_docente(dados_projeto),
    }


def _coautoria_docente(dados_projeto):
    partes = []
    for chave in ("orientador", "coorientador"):
        nome = _valor(dados_projeto, chave)
        if nome:
            partes.append(f"{nome} - Docente")
    return "; ".join(partes)


def _herdar(dados_ptt, contexto, *chaves, fallback=""):
    proprio = _valor(dados_ptt, *chaves)
    if proprio:
        return proprio
    return fallback


def formatar_ficha_22_itens(dados_ptt, dados_projeto=None):
    """Lista os 22 campos na ordem da Resolução 007/2025.

    Autoria, ano, coautoria, área, linha e projeto vazios herdam o trabalho.
    """
    dados_ptt = dados_ptt or {}
    ctx = _contexto(dados_projeto)
    return [
        ("I. Autoria", _herdar(dados_ptt, ctx, "autoria", fallback=ctx["autoria"])),
        ("II. Tipo de produção", _valor(dados_ptt, "tipo")),
        ("III. Subtipo de produção", _valor(dados_ptt, "subtipo", "subtipo_producao")),
        ("IV. Título", _valor(dados_ptt, "titulo")),
        ("V. Ano", _herdar(dados_ptt, ctx, "ano", fallback=ctx["ano"])),
        ("VI. Coautoria e categoria", _herdar(dados_ptt, ctx, "coautores", "coautoria", fallback=ctx["coautoria"])),
        ("VII. Área de concentração", _herdar(dados_ptt, ctx, "area_concentracao", fallback=ctx["area"])),
        ("VIII. Linha de pesquisa", _herdar(dados_ptt, ctx, "linha_pesquisa", fallback=ctx["linha"])),
        ("IX. Projeto de pesquisa", _herdar(dados_ptt, ctx, "projeto", fallback=ctx["projeto"])),
        ("X. Projeto com financiamento", _valor(dados_ptt, "financiamento")),
        ("XI. Financiador", _valor(dados_ptt, "financiador")),
        ("XII. Demanda", _valor(dados_ptt, "demanda")),
        ("XIII. Impacto", _valor(dados_ptt, "impacto")),
        ("XIV. Justificativa do Impacto", _valor(dados_ptt, "justificativa_impacto")),
        ("XV. Inovação", _valor(dados_ptt, "inovacao")),
        ("XVI. Justificativa da Inovação", _valor(dados_ptt, "justificativa_inovacao")),
        ("XVII. Complexidade", _valor(dados_ptt, "complexidade")),
        ("XVIII. Justificativa da Complexidade", _valor(dados_ptt, "justificativa_complexidade")),
        ("XIX. Validação do Produto", _valor(dados_ptt, "validacao")),
        ("XX. Modo de Divulgação", _valor(dados_ptt, "divulgacao_url", "divulgacao")),
        ("XXI. Abrangência ou Inserção Social", _valor(dados_ptt, "abrangencia")),
        ("XXII. Público Usuário", _valor(dados_ptt, "publico_usuario")),
    ]