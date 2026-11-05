# -*- coding: utf-8 -*-
"""Remove caracteres inválidos para OOXML e corrige escapes JSON problemáticos no mock."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOCK = ROOT / "frontend" / "src" / "fixtures" / "preenchimento-direto-mock.json"

_ILLEGAL = re.compile(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\uFFFE\uFFFF]")
_FRAC = re.compile(r"(?:\\frac|\x0crac|rac)\{([^}]*)\}\{([^}]*)\}")


def latex_plain(text: str) -> str:
    while True:
        novo, n = _FRAC.subn(r"(\1)/(\2)", text)
        text = novo
        if n == 0:
            break
    subs = (
        (r"\\cdot", "·"),
        (r"\\varepsilon", "ε"),
        (r"\\delta", "δ"),
        ("arepsilon", "ε"),
        (r"\\", ""),
    )
    for a, b in subs:
        text = text.replace(a, b)
    return text


def sanitizar(text: str) -> str:
    text = _ILLEGAL.sub("", text)
    text = latex_plain(text)
    return text


def walk(obj):
    if isinstance(obj, str):
        return sanitizar(obj)
    if isinstance(obj, dict):
        return {k: walk(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [walk(v) for v in obj]
    return obj


def main() -> None:
    data = json.loads(MOCK.read_text(encoding="utf-8"))
    fixed = walk(data)
    MOCK.write_text(json.dumps(fixed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Atualizado {MOCK}")


if __name__ == "__main__":
    main()
