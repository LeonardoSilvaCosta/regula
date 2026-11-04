"""Numeração, sumário e manuscrito exigidos pela Resolução nº 009/2025."""
import re

from .legendas import titulo_produto


BM_LISTA_ILUSTRACOES = "sec_lista_ilustracoes"
BM_LISTA_TABELAS = "sec_lista_tabelas"
BM_LISTA_SIGLAS = "sec_lista_siglas"
BM_LISTA_SIMBOLOS = "sec_lista_simbolos"

_SUBLISTAS_ILUSTRACAO = (
    "LISTA DE FIGURAS",
    "LISTA DE GRÁFICOS",
    "LISTA DE QUADROS",
    "LISTA DE TABELAS",
)

_TIPOS_ILUSTRACAO = (
    ("figura", "LISTA DE FIGURAS", "sec_lista_figuras"),
    ("gráfico", "LISTA DE GRÁFICOS", "sec_lista_graficos"),
    ("grafico", "LISTA DE GRÁFICOS", "sec_lista_graficos"),
    ("quadro", "LISTA DE QUADROS", "sec_lista_quadros"),
    ("tabela", "LISTA DE TABELAS", "sec_lista_tabelas"),
    ("desenho", "LISTA DE DESENHOS", "sec_lista_desenhos"),
    ("esquema", "LISTA DE ESQUEMAS", "sec_lista_esquemas"),
    ("fluxograma", "LISTA DE FLUXOGRAMAS", "sec_lista_fluxogramas"),
    ("fotografia", "LISTA DE FOTOGRAFIAS", "sec_lista_fotografias"),
    ("mapa", "LISTA DE MAPAS", "sec_lista_mapas"),
    ("organograma", "LISTA DE ORGANOGRAMAS", "sec_lista_organogramas"),
    ("planta", "LISTA DE PLANTAS", "sec_lista_plantas"),
)

_BLOCOS_MANUSCRITO = (
    ("resumo", "Resumo"),
    ("introducao", "Introdução"),
    ("metodologia", "Metodologia"),
    ("resultados", "Resultados parciais"),
    ("referencias", "Referências"),
)


def tem_hipotese(projeto):
    hipotese = (projeto or {}).get("hipotese")
    if isinstance(hipotese, str):
        return bool(hipotese.strip())
    if isinstance(hipotese, (list, tuple)):
        return any(str(item).strip() for item in hipotese)
    return bool(hipotese)


def numeracao_secoes(projeto):
    """Seções primárias sem lacuna. Hipóteses só entra quando há conteúdo."""
    numeros = {"consideracoes": 1, "objetivos": 2}
    proximo = 3
    if tem_hipotese(projeto):
        numeros["hipoteses"] = proximo
        proximo += 1
    numeros["metodologia"] = proximo
    proximo += 1
    numeros["produtos"] = proximo
    proximo += 1
    numeros["cronograma"] = proximo
    proximo += 1
    numeros["resultados"] = proximo
    return numeros


def eh_documental(projeto):
    projeto = projeto or {}
    tipo = (projeto.get("tipo_desenho") or "").strip().lower()
    return "documental" in tipo or "bibliogr" in tipo or bool(projeto.get("metodologia_fontes"))


def tipo_ilustracao(rotulo):
    primeira = str(rotulo or "").strip().split(" ", 1)[0].lower()
    primeira = primeira.rstrip(".:;—–-")
    for chave, titulo, bookmark in _TIPOS_ILUSTRACAO:
        if primeira == chave:
            return titulo, bookmark
    return "LISTA DE ILUSTRAÇÕES", BM_LISTA_ILUSTRACOES


def agrupar_ilustracoes(entradas):
    """Sublistas fixas do modelo: figuras, gráficos, quadros e tabelas."""
    grupos = {titulo: [] for titulo in _SUBLISTAS_ILUSTRACAO}
    for rotulo, bookmark in entradas:
        titulo, _bookmark_lista = tipo_ilustracao(rotulo)
        if titulo in grupos:
            grupos[titulo].append((rotulo, bookmark))
    return [(titulo, grupos[titulo]) for titulo in _SUBLISTAS_ILUSTRACAO]


def artigo_tem_conteudo(artigo):
    if not isinstance(artigo, dict) or not artigo:
        return False
    if artigo.get("resumo_estruturado") or artigo.get("resumo_topicos") or artigo.get("resumo"):
        return True
    if artigo.get("secoes_texto"):
        return True
    for chave in (
        "introducao", "metodologia", "metodo", "resultados_preliminares",
        "conclusao", "palavras_chave", "referencias",
    ):
        if str(artigo.get(chave) or "").strip():
            return True
    return False


def artigos_de(dados_resultados):
    if not isinstance(dados_resultados, dict):
        return []
    if isinstance(dados_resultados.get("artigos"), list) and dados_resultados["artigos"]:
        return [artigo for artigo in dados_resultados["artigos"] if isinstance(artigo, dict)]
    ordem = []
    if isinstance(dados_resultados.get("artigo_1"), dict):
        ordem.append(dados_resultados["artigo_1"])
    elif isinstance(dados_resultados.get("artigo_preliminar"), dict):
        ordem.append(dados_resultados["artigo_preliminar"])
    for indice in range(2, 10):
        artigo = dados_resultados.get(f"artigo_{indice}")
        if isinstance(artigo, dict):
            ordem.append(artigo)
    return ordem


def _secoes_artigo(artigo):
    secoes = []
    for secao in artigo.get("secoes_texto") or []:
        if isinstance(secao, (tuple, list)) and len(secao) >= 2:
            secoes.append((str(secao[0]).strip(), str(secao[1]).strip()))
        elif isinstance(secao, dict):
            titulo = str(secao.get("titulo") or secao.get("rotulo") or "").strip()
            texto = str(secao.get("texto") or secao.get("conteudo") or "").strip()
            secoes.append((titulo, texto))
    return secoes


def _achar_secao(secoes, usados, chaves):
    for indice, (titulo, texto) in enumerate(secoes):
        if indice in usados or not texto:
            continue
        baixo = titulo.lower()
        if any(chave in baixo for chave in chaves):
            usados.add(indice)
            return texto
    return ""


def _texto_referencias(artigo, secoes, usados):
    bruto = artigo.get("referencias")
    if isinstance(bruto, (list, tuple)):
        linhas = [str(item).strip() for item in bruto if str(item).strip()]
        if linhas:
            return "\n".join(linhas)
    elif str(bruto or "").strip():
        return str(bruto).strip()
    return _achar_secao(secoes, usados, ("referên", "referen"))


def blocos_manuscrito(artigo):
    """Resumo, introdução, metodologia, resultados parciais e referências."""
    artigo = artigo or {}
    secoes = _secoes_artigo(artigo)
    usados = set()
    topicos = artigo.get("resumo_topicos") or artigo.get("resumo_estruturado") or []
    resumo = str(artigo.get("resumo") or "").strip() or _achar_secao(secoes, usados, ("resumo",))
    introducao = str(artigo.get("introducao") or "").strip() or _achar_secao(secoes, usados, ("introdu",))
    metodologia = (
        str(artigo.get("metodologia") or artigo.get("metodo") or "").strip()
        or _achar_secao(secoes, usados, ("metodolog", "método", "metodo", "material"))
    )
    resultados = (
        str(artigo.get("resultados_preliminares") or "").strip()
        or _achar_secao(secoes, usados, ("resultado",))
    )
    referencias = _texto_referencias(artigo, secoes, usados)
    extras = []
    for indice, (titulo, texto) in enumerate(secoes):
        if indice in usados or not texto or _extra_omitido(titulo):
            continue
        extras.append((_sem_numero_de_artigo(titulo), texto))
    return {
        "topicos": topicos,
        "palavras_chave": str(artigo.get("palavras_chave") or "").strip(),
        "resumo": resumo,
        "introducao": introducao,
        "metodologia": metodologia,
        "resultados": resultados,
        "referencias": referencias,
        "extras": extras,
    }


def bloco_preenchido(blocos, chave):
    if chave == "resumo":
        return bool(blocos.get("topicos") or blocos.get("resumo") or blocos.get("palavras_chave"))
    return bool(str(blocos.get(chave) or "").strip())


_ROMANOS = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX")


def _titulo_artigo_informado(titulo):
    baixo = (titulo or "").strip().lower()
    return bool(baixo) and baixo not in ("resultados preliminares", "artigo")


def rotulo_artigo(numero, indice, artigo):
    """Identificação do produto bibliográfico no sumário e no corpo."""
    del numero
    titulo = (artigo.get("titulo") or "").strip()
    if titulo.lower().startswith("produto bibliográfico"):
        return titulo
    romano = _ROMANOS[indice - 1] if 1 <= indice <= len(_ROMANOS) else str(indice)
    base = f"Produto Bibliográfico {romano} - Artigo {indice}"
    if _titulo_artigo_informado(titulo):
        return f"{base} – {titulo}"
    return base


def rotulo_pos(prefixo, indice, total, rotulo):
    """Título em maiúsculas. Vários itens recebem letra."""
    texto = str(rotulo or "").strip()
    cabeca = prefixo if total <= 1 else f"{prefixo} {chr(ord('A') + indice - 1)}"
    if not texto:
        return cabeca
    if texto.upper().startswith(prefixo):
        return texto.upper()
    return f"{cabeca} – {texto}".upper()


def itens_do_sumario(dados, apendices=None, anexos=None, listas=None):
    """Listas utilizadas, depois a parte textual. Capa, rosto e aprovação ficam de fora."""
    projeto = (dados or {}).get("projeto") or {}
    numeros = numeracao_secoes(projeto)
    itens = [(titulo, bookmark) for titulo, bookmark in (listas or [])]

    n1 = numeros["consideracoes"]
    n2 = numeros["objetivos"]
    itens.extend([
        ("APRESENTAÇÃO", "sec_apresentacao"),
        (f"{n1}. CONSIDERAÇÕES GERAIS", "sec_1"),
        (f"{n1}.1. INTRODUÇÃO", "sec_1_1"),
        (f"{n1}.2. JUSTIFICATIVA", "sec_1_2"),
        (f"{n1}.3. PROBLEMA DE PESQUISA", "sec_1_3"),
        (f"{n1}.4. REVISÃO DA LITERATURA / REFERENCIAL TEÓRICO", "sec_1_4"),
        (f"{n2}. OBJETIVOS", "sec_2"),
        (f"{n2}.1. OBJETIVO GERAL", "sec_2_1"),
        (f"{n2}.2. OBJETIVOS ESPECÍFICOS", "sec_2_2"),
    ])
    if "hipoteses" in numeros:
        nh = numeros["hipoteses"]
        itens.append((f"{nh}. HIPÓTESES OU QUESTÕES NORTEADORAS", "sec_hipoteses"))

    nm = numeros["metodologia"]
    itens.append((f"{nm}. METODOLOGIA", "sec_metodologia"))
    itens.append((f"{nm}.1. NATUREZA DA PESQUISA", "sec_met_1"))
    if projeto.get("metodologia_locus") or not eh_documental(projeto):
        itens.append((f"{nm}.2. LÓCUS", "sec_met_2"))
    if eh_documental(projeto):
        itens.append((f"{nm}.3. FONTES DE DADOS", "sec_met_3f"))
    else:
        itens.append((f"{nm}.3. PARTICIPANTES E COORTE POPULACIONAL", "sec_met_3p"))
    itens.append((f"{nm}.4. PROCEDIMENTOS DE COLETA", "sec_met_4"))
    if not eh_documental(projeto) or projeto.get("metodologia_etica"):
        itens.append((f"{nm}.5. PROCEDIMENTOS ÉTICOS", "sec_met_5"))
    itens.append((f"{nm}.6. ANÁLISE DE DADOS", "sec_met_6"))

    np = numeros["produtos"]
    itens.append((f"{np}. PROPOSTA DE PRODUTOS", "sec_produtos"))
    for indice, ptt in enumerate(projeto.get("ptts") or [], start=1):
        itens.append((titulo_produto(indice, ptt, np), f"sec_prod_{indice}"))

    nc = numeros["cronograma"]
    nr = numeros["resultados"]
    itens.append((f"{nc}. CRONOGRAMA", "sec_cronograma"))
    itens.append((f"{nr}. RESULTADOS PRELIMINARES", "sec_resultados"))
    for indice, artigo in enumerate(artigos_de((dados or {}).get("resultados")), start=1):
        if artigo_tem_conteudo(artigo):
            itens.append((rotulo_artigo(nr, indice, artigo), f"sec_res_{indice}"))

    itens.append(("REFERÊNCIAS", "sec_referencias"))
    total_ap = len(apendices or [])
    for indice, item in enumerate(apendices or [], start=1):
        rotulo = item[0] if isinstance(item, (tuple, list)) else str(item)
        itens.append((rotulo_pos("APÊNDICE", indice, total_ap, rotulo), f"pos_apendice_{indice}"))
    total_an = len(anexos or [])
    for indice, item in enumerate(anexos or [], start=1):
        rotulo = item[0] if isinstance(item, (tuple, list)) else str(item)
        itens.append((rotulo_pos("ANEXO", indice, total_an, rotulo), f"pos_anexo_{indice}"))
    return itens


def nomes_blocos_ausentes(artigo):
    blocos = blocos_manuscrito(artigo)
    ausentes = []
    for chave, rotulo in _BLOCOS_MANUSCRITO:
        if not bloco_preenchido(blocos, chave):
            ausentes.append(rotulo)
    return ausentes


def texto_problema(projeto):
    bruto = (projeto or {}).get("problema")
    if isinstance(bruto, (list, tuple)):
        return " ".join(str(item).strip() for item in bruto if str(item).strip())
    return str(bruto or "").strip()


def verbos_repetidos_quadro(linhas):
    """Verbo inicial de cada objetivo específico do Quadro 1."""
    vistos = {}
    for linha in linhas or []:
        if not isinstance(linha, (list, tuple)) or len(linha) < 3:
            continue
        for parte in re.split(r"[\n;]", str(linha[2])):
            verbo = _verbo_inicial(parte)
            if not verbo:
                continue
            vistos.setdefault(verbo, 0)
            vistos[verbo] += 1
    return sorted(verbo for verbo, quantidade in vistos.items() if quantidade > 1)


def _verbo_inicial(texto):
    limpo = re.sub(
        r"^\s*\(?\s*(?:i{1,3}|iv|vi{0,3}|ix|x|\d+)\s*[\).\]]\s*",
        "",
        str(texto or "").strip(),
        flags=re.IGNORECASE,
    )
    palavras = re.findall(r"[A-Za-zÀ-ÿ-]+", limpo)
    if not palavras:
        return ""
    return palavras[0].lower()


def _extra_omitido(titulo):
    baixo = str(titulo or "").lower()
    return any(
        trecho in baixo
        for trecho in ("conclus", "considerações finais", "consideracoes finais")
    )


def _sem_numero_de_artigo(titulo):
    return re.sub(r"^\s*\d+(?:\.\d+)*\.?\s+", "", str(titulo or "")).strip()


def citacoes_longas(texto):
    achados = []
    for miolo in re.findall(r"[\"“«](.+?)[\"”»]", texto or "", flags=re.S):
        trecho = miolo.strip()
        if trecho.count("\n") + 1 > 3 or len(trecho) > 280:
            achados.append(re.sub(r"\s+", " ", trecho)[:140])
    return achados
