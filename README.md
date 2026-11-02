# Padronizador PPGSP/UFPA

Monorepo do padronizador de documentos acadêmicos (Resoluções 007, 009 e 010).

## Estrutura

| Pasta | Conteúdo |
|-------|----------|
| `backend/` | CLI Python, geradores `.docx`, `inputs/`, `outputs/`, `assets/` |
| *(futuro)* `frontend/` | Interface web |

A raiz concentra configuração compartilhada (`.gitignore`, documentação). **O ponto de entrada da CLI fica em `backend/main.py`.**

## Backend (CLI)

Ambiente virtual na raiz ou em `backend/` (recomendado: raiz, como hoje):

```powershell
cd backend
python -m venv ..\.venv   # apenas na primeira vez, se usar .venv na raiz
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Gerar relatório de qualificação (caminhos relativos a `backend/`):

```powershell
cd backend
python main.py qualificacao -i inputs/qualificacao/projeto.docx -o outputs/qualificacao/Relatorio_Qualificacao_Final.docx -n mestrado
```

Comandos: `qualificacao`, `dissertacao`, `tese`. Use `python main.py --help` para opções.
