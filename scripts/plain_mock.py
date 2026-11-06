# -*- coding: utf-8 -*-
"""Converte restos de Markdown no mock para texto corrido."""
import json
import re
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "frontend" / "src" / "fixtures" / "preenchimento-direto-mock.json"
data = json.loads(p.read_text(encoding="utf-8"))

BT = "`"


def md_inline(s: str) -> str:
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", s)
    s = re.sub(BT + r"([^" + BT + r"]+)" + BT, r"\1", s)
    return s


def table_to_text(lines: list[str]):
    rows = []
    for line in lines:
        if ":---" in line or re.search(r"\|\s*:?-{3,}", line):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cols)
    if len(rows) < 2:
        return " ".join(md_inline(line) for line in lines)
    header = rows[0]
    out = []
    for row in rows[1:]:
        bits = []
        for h, c in zip(header, row):
            c = md_inline(c).strip()
            if not c:
                continue
            bits.append(f"{h}: {c}")
        if bits:
            sentence = ". ".join(bit.rstrip(".") for bit in bits)
            out.append(sentence + ".")
    return out


def transform(s: str):
    if "|" not in s:
        return md_inline(s)
    lines = s.split("\n")
    if not any(line.strip().startswith("|") for line in lines):
        return md_inline(s)
    parts: list[str] = []
    buf: list[str] = []
    table: list[str] = []

    def flush_table():
        nonlocal table
        if not table:
            return
        conv = table_to_text(table)
        if isinstance(conv, list):
            parts.extend(conv)
        elif conv.strip():
            parts.append(conv)
        table = []

    def flush_buf():
        nonlocal buf
        if not buf:
            return
        text = md_inline("\n".join(buf)).strip()
        if text:
            parts.append(text)
        buf = []

    for line in lines:
        if line.strip().startswith("|"):
            flush_buf()
            table.append(line)
        else:
            flush_table()
            buf.append(line)
    flush_buf()
    flush_table()
    if len(parts) == 1:
        return parts[0]
    return parts


def walk(o):
    if isinstance(o, str):
        return transform(o)
    if isinstance(o, list):
        out = []
        for item in o:
            result = walk(item)
            if isinstance(item, str) and isinstance(result, list):
                out.extend(result)
            else:
                out.append(result)
        return out
    if isinstance(o, dict):
        return {k: walk(v) for k, v in o.items()}
    return o


new = walk(data)
text = json.dumps(new, ensure_ascii=False, indent=2) + "\n"
text = text.replace(".. ", ". ")
p.write_text(text, encoding="utf-8")
print("backticks", text.count(BT))
print("italics", len(re.findall(r"\*[^*]+\*", text)))
print("md rows", sum(1 for line in text.splitlines() if line.strip().startswith('"|')))
