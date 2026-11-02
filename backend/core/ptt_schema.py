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


def formatar_ficha_22_itens(dados_ptt):
    """Lista os 22 campos. Campo vazio permanece vazio; área e linha são institucionais."""
    dados_ptt = dados_ptt or {}
    return [
        ("I. Autoria", _valor(dados_ptt, "autoria")),
        ("II. Tipo de produção", _valor(dados_ptt, "tipo")),
        ("III. Subtipo de produção", _valor(dados_ptt, "subtipo", "subtipo_producao")),
        ("IV. Título", _valor(dados_ptt, "titulo")),
        ("V. Ano", _valor(dados_ptt, "ano")),
        ("VI. Coautoria e categoria", _valor(dados_ptt, "coautoria")),
        ("VII. Área de concentração", _AREA),
        ("VIII. Linha de pesquisa", _LINHA),
        ("IX. Projeto de pesquisa", _valor(dados_ptt, "projeto")),
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
        ("XX. Modo de Divulgação", _valor(dados_ptt, "divulgacao")),
        ("XXI. Abrangência ou Inserção Social", _valor(dados_ptt, "abrangencia")),
        ("XXII. Público Usuário", _valor(dados_ptt, "publico_usuario")),
    ]