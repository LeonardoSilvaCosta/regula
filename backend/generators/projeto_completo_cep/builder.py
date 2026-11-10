"""Projeto Completo CEP com capa, folha de rosto e corpo no padrão da qualificação."""
import re

import docx
from docx.enum.section import WD_SECTION

from core.atualizar_campos import atualizar_campos_word
from core.styles import (
    apply_base_styles,
    aplicar_cabecalho_institucional,
    aplicar_idioma_pt_br,
    aplicar_rodape_local_ano,
    limpar_rodape,
)
from generators.common.referencias import renderizar_referencias
from generators.qualificacao.builder import (
    _paginar,
    _secao_sem_numero,
    habilitar_atualizacao_campos,
)
from generators.qualificacao.formato import adicionar_lacuna, adicionar_paragrafo, adicionar_titulo
from generators.qualificacao.pre_textual.capa import build_capa
from generators.qualificacao.pre_textual.folha_rosto import build_folha_rosto
from generators.qualificacao.textual.cronograma import build_cronograma

TEXTO_NATUREZA = (
    "Projeto Detalhado de Pesquisa apresentado ao Comitê de Ética em Pesquisa do Instituto de "
    "Ciências da Saúde da Universidade Federal do Pará (CEP/ICS/UFPA) e ao Colegiado do Programa "
    "de Pós-Graduação em Segurança Pública (PPGSP/ICEN/UFPA), vinculado ao desenvolvimento da "
    "Dissertação de Mestrado Profissional em Segurança Pública."
)
_RE_SUBTITULO = re.compile(r"^\d+\.\d+(?:\.\d+)?\.?\s+\S")


def _lista(valor):
    if valor is None:
        return []
    if isinstance(valor, (list, tuple)):
        return [str(item).strip() for item in valor if str(item).strip()]
    texto = str(valor).strip()
    return [texto] if texto else []


def _corpo(doc, valor):
    paragrafos = _lista(valor)
    if not paragrafos:
        adicionar_lacuna(doc, "[Preencher]")
        return
    for paragrafo in paragrafos:
        if _RE_SUBTITULO.match(paragrafo):
            adicionar_titulo(doc, paragrafo, primario=False)
        else:
            adicionar_paragrafo(doc, paragrafo)


def gerar_documento_projeto_completo_cep(
    caminho_saida,
    revisao=None,
    nivel="mestrado",
    assets_dir="assets",
):
    dados = revisao or {}
    meta = dict(dados.get("metadata") or {})
    meta["nivel"] = str(nivel or meta.get("nivel") or "mestrado").strip().lower()
    secoes = dados.get("sections") or {}
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

    textual = doc.add_section(WD_SECTION.NEW_PAGE)
    limpar_rodape(textual)
    _paginar(textual, "decimal", inicio=1)

    if _lista(secoes.get("resumo")) or str(secoes.get("palavras_chave") or "").strip():
        adicionar_titulo(doc, "RESUMO")
        _corpo(doc, secoes.get("resumo"))
        palavras = str(secoes.get("palavras_chave") or "").strip()
        if palavras:
            adicionar_paragrafo(doc, f"Palavras-chave: {palavras}")

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
        _corpo(doc, cronograma_texto)
    else:
        projeto = {
            "cronograma": dados.get("cronograma") or [],
            "ano": ano,
        }
        build_cronograma(doc, projeto, nivel=meta["nivel"], ano_referencia=ano, numero=8)

    adicionar_titulo(doc, "9. ORÇAMENTO")
    _corpo(doc, secoes.get("orcamento"))

    renderizar_referencias(doc, _lista(secoes.get("referencias")))
    aplicar_idioma_pt_br(doc)
    habilitar_atualizacao_campos(doc)
    doc.save(caminho_saida)
    atualizar_campos_word(caminho_saida)
    return caminho_saida
