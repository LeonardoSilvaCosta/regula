"""Monta o Protocolo CEP como documento com um bloco por campo."""
import docx
from docx.shared import Pt

from core.styles import apply_base_styles
from generators.protocolo_cep.estrutura import CAMPOS


def _texto(valor):
    if valor is None:
        return ""
    if isinstance(valor, (list, tuple)):
        return "\n".join(str(item).strip() for item in valor if str(item).strip())
    return str(valor).strip()


def gerar_documento_protocolo_cep(caminho_saida, protocolo=None, **_ignorado):
    """Escreve cada campo do formulário, na ordem da estrutura, mesmo vazio."""
    dados = protocolo or {}
    doc = docx.Document()
    apply_base_styles(doc)

    titulo = doc.add_paragraph()
    titulo.paragraph_format.space_after = Pt(12)
    run = titulo.add_run("PROTOCOLO CEP")
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)

    for chave, rotulo, _tipo in CAMPOS:
        cabeca = doc.add_paragraph()
        cabeca.paragraph_format.space_before = Pt(10)
        cabeca.paragraph_format.space_after = Pt(2)
        marca = cabeca.add_run(rotulo)
        marca.bold = True
        marca.font.name = "Times New Roman"
        marca.font.size = Pt(12)

        corpo = doc.add_paragraph()
        corpo.paragraph_format.space_after = Pt(4)
        conteudo = _texto(dados.get(chave)) or "—"
        texto = corpo.add_run(conteudo)
        texto.font.name = "Times New Roman"
        texto.font.size = Pt(12)

    doc.save(caminho_saida)
    return caminho_saida
