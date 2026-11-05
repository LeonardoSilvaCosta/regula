# -*- coding: utf-8 -*-
"""Gera preenchimento-direto-mock.json a partir do relatório Markdown."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = Path(
    r"c:\Users\sirco\.cursor\projects\c-Users-sirco-Documents-Mestrado-Padronizador-de-disserta-o"
    r"\attachments\d36563dc-20b3-406d-96e6-c765c652fb61\relatorio_qualificacao_ppgsp_leonardo_costa.md"
)
OUT = ROOT / "frontend" / "src" / "fixtures" / "preenchimento-direto-mock.json"

PROJETO_PTT = (
    "Modelos de Inteligência Artificial e Métodos Quantitativos Aplicados "
    "à Gestão e Saúde Ocupacional na Segurança Pública"
)


def load() -> str:
    return MD.read_text(encoding="utf-8")


def _latex_inline_para_texto(expr: str) -> str:
    expr = expr.replace("{,}", ",")
    while True:
        expr, n = re.subn(r"\\frac\{([^}]*)\}\{([^}]*)\}", r"(\1)/(\2)", expr)
        if n == 0:
            break
    for token, repl in (
        (r"\cdot", "·"),
        (r"\varepsilon", "ε"),
        (r"\delta", "δ"),
    ):
        expr = expr.replace(token, repl)
    expr = expr.replace("\\", "")
    return expr


def clean(text: str) -> str:
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(
        r"\$([^$]+)\$",
        lambda m: _latex_inline_para_texto(m.group(1)),
        text,
    )
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]", "", text)
    return text.strip()


def slice_between(text: str, start: str, end: str | None) -> str:
    i = text.find(start)
    if i < 0:
        return ""
    i += len(start)
    if end:
        j = text.find(end, i)
        if j < 0:
            return text[i:]
        return text[i:j]
    return text[i:]


def paragraphs(block: str) -> list[str]:
    block = clean(block)
    parts = [p.strip() for p in re.split(r"\n\s*\n", block) if p.strip()]
    out: list[str] = []
    for p in parts:
        p = re.sub(r"^#{1,6}\s+", "", p, flags=re.MULTILINE)
        p = re.sub(r"^>\s*", "", p, flags=re.MULTILINE)
        p = re.sub(r"^[-•]\s+", "", p, flags=re.MULTILINE)
        if p.startswith("|") or p.startswith("```"):
            continue
        if len(p) > 20:
            out.append(p)
    return out


def parse_siglas(text: str) -> list[list[str]]:
    siglas: list[list[str]] = []
    block = slice_between(text, "## 6. LISTA DE ABREVIATURAS E SIGLAS", "## 7. LISTA DE SÍMBOLOS")
    for line in block.splitlines():
        if "|" not in line or ":---" in line:
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) < 2:
            continue
        sigla = clean(parts[0])
        significado = clean(parts[1])
        if not sigla or sigla.lower() == "sigla":
            continue
        siglas.append([sigla, significado])
    return siglas


def parse_referencias(text: str) -> list[str]:
    block = slice_between(text, "## 1. REFERÊNCIAS", "---")
    refs: list[str] = []
    for chunk in re.split(r"\n\s*\n", block):
        chunk = clean(chunk)
        if len(chunk) > 40 and re.match(r"^[A-ZÁÉÍÓÚÂÊÔÃÕÇ]", chunk):
            refs.append(chunk)
    return refs


def parse_cronograma(text: str) -> list[dict]:
    """Extrai meses marcados com X na tabela do cronograma."""
    block = slice_between(text, "## 6. CRONOGRAMA", "## 7. RESULTADOS")
    rows: list[dict] = []
    for line in block.splitlines():
        if not line.strip().startswith("|"):
            continue
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if not cols or cols[0].lower().startswith(":---"):
            continue
        nome = re.sub(r"\*\*", "", cols[0]).strip()
        if not nome or nome.lower().startswith("atividade"):
            continue
        meses: list[int] = []
        for idx, cell in enumerate(cols[1:], start=1):
            if "**X**" in cell or cell.upper() == "X":
                meses.append(idx)
        if nome:
            rows.append({"nome": nome, "meses": meses})
    return rows


def parse_objetivos_especificos(block: str) -> list[str]:
    items: list[str] = []
    for m in re.finditer(
        r"^\d+\.\s+\*\*([^*]+)\*\*\s*(.+)$", block, flags=re.MULTILINE
    ):
        verbo = m.group(1).strip()
        resto = m.group(2).strip()
        items.append(f"{verbo} {resto}")
    return items


def _ptt_field(sec: str, roman: str, label: str, multiline: bool = False) -> str:
    pat = (
        rf"{roman}\.\s*\*\*{re.escape(label)}:?\*\*\s*(.+?)"
        rf"(?=\n(?:[IVXLC]+|[A-Z]{{1,4}})\.\s*\*\*|\n---|\Z)"
    )
    m = re.search(pat, sec, re.DOTALL | re.IGNORECASE)
    if not m:
        return ""
    val = clean(m.group(1))
    if not multiline:
        val = val.split("\n")[0].strip()
    return val


def parse_ptt(text: str) -> list[dict]:
    produtos: list[dict] = []
    bloco = slice_between(text, "## 5. PROPOSTA DE PRODUTOS", "## 6. CRONOGRAMA")
    for num, nome_curto, body in re.findall(
        r"### 5\.(\d+)\. PRODUTO \d+:\s*(.+?)\n(.*?)(?=### 5\.\d+\. PRODUTO|\Z)",
        bloco,
        flags=re.DOTALL,
    ):

        impacto = _ptt_field(body, "XIII", "Impacto")
        inovacao = _ptt_field(body, "XV", "Inovação")
        complexidade = _ptt_field(body, "XVII", "Complexidade")

        produtos.append(
            {
                "num": num,
                "nome": nome_curto[:120],
                "autoria": "Leonardo da Silva Costa",
                "tipo": _ptt_field(body, "II", "Tipo de produção") or _ptt_field(body, "II", "Tipo de producao"),
                "subtipo": _ptt_field(body, "III", "Subtipo de produção") or _ptt_field(body, "III", "Subtipo de producao"),
                "titulo": _ptt_field(body, "IV", "Título") or _ptt_field(body, "IV", "Titulo") or nome_curto,
                "ano": _ptt_field(body, "V", "Ano") or "2026",
                "coautoria": "Prof. Dr. Edson Marcos Leal Soares Ramos (Docente); Prof. Dr. Renato Hidaka Torres (Docente)",
                "projeto": PROJETO_PTT,
                "financiamento": "Não",
                "financiador": "",
                "demanda": _ptt_field(body, "XII", "Demanda") or "Espontânea",
                "impacto": impacto or "Médio",
                "justificativa_impacto": _ptt_field(body, "XIV", "Justificativa do Impacto – até 50 palavras", True)[:500]
                or _ptt_field(body, "XIV", "Justificativa do Impacto", True)[:500],
                "inovacao": inovacao or "Médio",
                "justificativa_inovacao": _ptt_field(body, "XVI", "Justificativa da Inovação – até 50 palavras", True)[:500]
                or _ptt_field(body, "XVI", "Justificativa da Inovação", True)[:500],
                "complexidade": ("Alta" if complexidade.lower() == "alto" else complexidade) or "Média",
                "justificativa_complexidade": _ptt_field(body, "XVIII", "Justificativa da Complexidade – até 50 palavras", True)[:500]
                or _ptt_field(body, "XVIII", "Justificativa da Complexidade", True)[:500],
                "validacao": _ptt_field(body, "XIX", "Validação do Produto", True)[:400],
                "divulgacao": _ptt_field(body, "XX", "Modo de Divulgação", True)[:400],
                "abrangencia": (_ptt_field(body, "XXI", "Abrangência ou Inserção Social", True)[:120] or "Estadual"),
                "publico_usuario": _ptt_field(body, "XXII", "Público Usuário", True)[:400],
            }
        )
    return produtos


def main() -> None:
    raw = load()
    parte2 = slice_between(raw, "# PARTE II", "# PARTE III")
    if not parte2:
        parte2 = raw

    apresentacao = paragraphs(
        slice_between(parte2, "# APRESENTAÇÃO", "# 2. PROJETO DE QUALIFICAÇÃO")
    )
    proj = slice_between(parte2, "# 2. PROJETO DE QUALIFICAÇÃO", None)

    introducao = paragraphs(
        slice_between(proj, "### 1.1. INTRODUÇÃO", "### 1.2. JUSTIFICATIVA")
    )
    justificativa = paragraphs(
        slice_between(proj, "### 1.2. JUSTIFICATIVA", "### 1.3. PROBLEMA")
    )
    problema = paragraphs(
        slice_between(proj, "### 1.3. PROBLEMA", "### 1.4. REVISÃO")
    )
    revisao = paragraphs(
        slice_between(proj, "### 1.4. REVISÃO", "## 2. OBJETIVOS")
    )

    obj_block = slice_between(proj, "## 2. OBJETIVOS", "## 3. HIPÓTESES")
    og_m = re.search(
        r"### 2\.1\. OBJETIVO GERAL\s*\n\s*\n(.+?)(?=\n### 2\.2|\Z)",
        obj_block,
        re.DOTALL,
    )
    objetivo_geral = clean(og_m.group(1)) if og_m else ""
    objetivos_especificos = parse_objetivos_especificos(
        slice_between(obj_block, "### 2.2. OBJETIVOS ESPECÍFICOS", None)
    )

    hip_block = slice_between(proj, "## 3. HIPÓTESES", "## 4. METODOLOGIA")
    hipotese = paragraphs(hip_block)

    met_block = slice_between(proj, "## 4. METODOLOGIA", "## 5. PROPOSTA")
    metodologia_natureza = paragraphs(
        slice_between(met_block, "### 4.1. NATUREZA", "### 4.2.")
    )
    metodologia_locus = clean(
        slice_between(met_block, "### 4.2. LÓCUS", "### 4.3.")[:800]
    )
    metodologia_participantes = paragraphs(
        slice_between(met_block, "### 4.3.", "### 4.4.")
    )
    metodologia_fontes = paragraphs(
        "O acervo informacional integra dados primários secundarizados provenientes do banco relacional "
        "transacional do sistema CIAP WEB (PostgreSQL), articulando variáveis estruturadas tabulares "
        "e anotações narrativas de evolução clínica em texto livre."
    )
    metodologia_coleta = paragraphs(
        slice_between(met_block, "### 4.4. PROCEDIMENTOS DE COLETA", "### 4.5.")
    )
    metodologia_etica = paragraphs(
        slice_between(met_block, "### 4.5. PROCEDIMENTOS ÉTICOS", "### 4.6.")
    )
    metodologia_analise = paragraphs(
        slice_between(met_block, "### 4.6. ANÁLISE DE DADOS", "---")
    )

    # Tabelas amostrais (valores do relatório)
    tabela_1 = {
        "linhas": [
            ["1. Psiquiátrico Agudo (Ideação, Tentativa, Surto)", "149", "2,6%", "9", "60", "Nível 3 (Crise Aguda)"],
            ["2. Risco Moderado / Afastamento / Incidente", "1.432", "25,1%", "90", "90", "Nível 2 (Risco Moderado)"],
            ["3. Avaliações Psicológicas Adm. (sem afastamento)", "738", "12,9%", "47", "65", "Nível 0 (Adaptado)"],
            ["4. Clínico Ambulatorial Sintomático", "1.624", "28,5%", "103", "95", "Níveis 1 e 2"],
            ["5. Rotina Geral / Suporte Assistencial", "1.763", "30,9%", "111", "50", "Níveis 0 e 1"],
            ["Total Geral da Coorte Viva PMPA", "5.706", "100,0%", "360", "360", "Matriz equilibrada"],
        ]
    }
    tabela_2 = {
        "linhas": [
            ["1. Psiquiátrico Agudo", "149", "22", "43", "109", "194", "267", "447", "768", "> 504", "5 (3,4%)"],
            ["2. Risco Moderado / Afastamento", "1.432", "4", "13", "45", "108", "201", "455", "1.306", "> 435", "81 (5,7%)"],
            ["3. Avaliações Administrativas", "738", "4", "7", "13", "23", "42", "366", "1.217", "> 86", "134 (18,2%)"],
            ["4. Clínico Ambulatorial Sintomático", "1.624", "4", "18", "63", "124", "211", "400", "1.219", "> 434", "59 (3,6%)"],
            ["5. Rotina Geral / Suporte", "1.763", "6", "21", "59", "109", "186", "362", "2.083", "> 377", "77 (4,4%)"],
        ]
    }

    ptts = parse_ptt(proj)
    if len(ptts) < 4:
        ptts = parse_ptt(raw)

    altos = sum(1 for p in ptts if str(p.get("impacto", "")).lower() == "alto")
    total_ptt = len(ptts)
    prop = (altos / total_ptt) if total_ptt else 0

    titulo = (
        "Modelos de aprendizado de máquina multimodais para predição de desfechos "
        "relacionados à saúde mental de policiais militares do Pará a partir de "
        "prontuários psicossociais"
    )

    mock = {
        "documento_id": "",
        "tipo_documento": "qualificacao",
        "nivel": "mestrado",
        "metadata": {
            "titulo": titulo,
            "subtitulo": "",
            "autor": "Leonardo da Silva Costa",
            "orientador": "Prof. Dr. Edson Marcos Leal Soares Ramos",
            "coorientador": "Prof. Dr. Renato Hidaka Torres",
            "coordenador": "Prof. Dr. Edson Marcos Leal Soares Ramos",
            "ano": "2026",
            "local": "Belém-Pará",
            "area_concentracao": "Segurança Pública, Justiça, Conflitos e Cidadania",
            "linha_pesquisa": "Políticas, Gestão, Direitos Humanos, Criminalidade e Tecnologia da Informação",
            "data_aprovacao": "Belém, Pará, 15 de dezembro de 2026.",
        },
        "sections": {
            "apresentacao": apresentacao,
            "introducao": introducao,
            "justificativa": justificativa,
            "problema": problema,
            "revisao": revisao,
            "objetivo_geral": objetivo_geral,
            "objetivos_especificos": objetivos_especificos,
            "hipotese": hipotese,
            "metodologia_natureza": metodologia_natureza,
            "metodologia_locus": metodologia_locus,
            "metodologia_participantes": metodologia_participantes,
            "metodologia_fontes": metodologia_fontes,
            "metodologia_coleta": metodologia_coleta,
            "metodologia_etica": metodologia_etica,
            "metodologia_analise": metodologia_analise,
            "tabela_1": tabela_1,
            "tabela_2": tabela_2,
            "referencias": parse_referencias(raw),
        },
        "banca": [
            {
                "nome": "Prof. Dr. Edson Marcos Leal Soares Ramos",
                "titulacao": "Doutor",
                "instituicao": "Universidade Federal do Pará",
                "funcao": "Orientador(a)",
            },
            {
                "nome": "Prof. Dr. Renato Hidaka Torres",
                "titulacao": "Doutor",
                "instituicao": "Universidade Federal do Pará",
                "funcao": "Coorientador(a)",
            },
            {
                "nome": "Prof. Dr. Carlos Eduardo Lima",
                "titulacao": "Doutor",
                "instituicao": "Universidade Federal do Pará",
                "funcao": "Avaliador(a) Interno(a)",
            },
            {
                "nome": "Prof. Dr. Membro Externo da Banca",
                "titulacao": "Doutor",
                "instituicao": "Polícia Militar do Pará / Instituição Convidada",
                "funcao": "Avaliador(a) Externo(a)",
            },
        ],
        "siglas": parse_siglas(raw),
        "ptts": ptts,
        "cronograma": parse_cronograma(raw),
        "lacunas": [],
        "conformidade_ptt": {
            "valido": prop >= 0.5 and total_ptt >= 4,
            "total": total_ptt,
            "prop_alta": prop,
            "mensagem": f"Mock gerado a partir de {MD.name} ({total_ptt} PTTs, {altos} impacto Alto).",
        },
    }

    OUT.write_text(json.dumps(mock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Escrito {OUT}")
    print(f"  apresentacao: {len(apresentacao)}")
    print(f"  introducao: {len(introducao)}")
    print(f"  objetivos: {len(objetivos_especificos)}")
    print(f"  ptts: {total_ptt}")
    print(f"  refs: {len(mock['sections']['referencias'])}")
    print(f"  siglas: {len(mock['siglas'])}")
    print(f"  cronograma: {len(mock['cronograma'])}")


if __name__ == "__main__":
    main()
