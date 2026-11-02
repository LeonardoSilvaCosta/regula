"""Guarda o .docx enviado no passo de análise para a geração usar o mesmo arquivo."""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from uuid import uuid4

_DIR = Path(tempfile.gettempdir()) / "padronizador-ppgsp-uploads"
_ID = re.compile(r"^[0-9a-f]{32}$")


def guardar(conteudo: bytes) -> str:
    _DIR.mkdir(parents=True, exist_ok=True)
    documento_id = uuid4().hex
    (_DIR / f"{documento_id}.docx").write_bytes(conteudo)
    return documento_id


def caminho(documento_id: str) -> Path:
    if not _ID.fullmatch(documento_id or ""):
        raise FileNotFoundError("Documento de origem não encontrado. Analise o arquivo novamente.")
    arquivo = _DIR / f"{documento_id}.docx"
    if not arquivo.is_file():
        raise FileNotFoundError("Documento de origem não encontrado. Analise o arquivo novamente.")
    return arquivo
