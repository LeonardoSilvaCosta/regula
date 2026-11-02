# Padronizador PPGSP/UFPA

Monorepo que padroniza documentos acadêmicos do PPGSP (Resoluções 007, 009 e 010). O **backend** (FastAPI) expõe a API e a CLI que geram os `.docx`. O **frontend** (Next.js) é o assistente web de upload, revisão e exportação.

## Estrutura

| Pasta | Conteúdo |
|-------|----------|
| `backend/` | API FastAPI (`app/`), CLI (`main.py`), geradores, `inputs/`, `outputs/`, `assets/` |
| `frontend/` | Interface Next.js |
| `docker-compose.yml` | Backend na porta 8000 e frontend na porta 3000 |
| `Makefile` | Atalhos `build`, `up`, `down`, `logs`, `gen-types`, `cli-test` |

A raiz concentra a orquestração. O ponto de entrada da CLI continua em `backend/main.py`. A API sobe com `uvicorn app.main:app`.

## Docker (recomendado)

Na raiz do repositório, com Docker em execução:

```bash
make up
```

Equivalente: `docker compose up --build -d`.

- Interface: [http://localhost:3000](http://localhost:3000)
- API: [http://localhost:8000](http://localhost:8000) (`/health`, `/docs`)

O navegador chama a API em `http://localhost:8000` (variável `NEXT_PUBLIC_API_URL`, gravada na imagem no build). Para outro endereço público, defina a variável e reconstrua o frontend:

```bash
NEXT_PUBLIC_API_URL=https://api.exemplo.edu.br docker compose up --build -d
```

Outros atalhos:

| Comando | Efeito |
|---------|--------|
| `make build` | `docker compose build` |
| `make logs` | Logs em tempo real |
| `make down` | Para e remove os containers |
| `make gen-types` | Regenera `frontend/src/types/api.ts` (API em `127.0.0.1:8000`) |
| `make cli-test` | `python main.py --help` dentro da imagem do backend |

Hot-reload local (opcional):

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## Desenvolvimento nativo

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

CLI (caminhos relativos a `backend/`):

```powershell
cd backend
python main.py qualificacao -i inputs/qualificacao/projeto.docx -o outputs/qualificacao/Relatorio_Qualificacao_Final.docx -n mestrado
```

Comandos: `qualificacao`, `dissertacao`, `tese`. Use `python main.py --help` para as opções.

Frontend (com a API já no ar):

```powershell
cd frontend
npm ci
npm run dev
```

A interface fica em [http://localhost:3000](http://localhost:3000). Para regenerar os tipos a partir do OpenAPI:

```powershell
cd frontend
npm run gen:types
```

## Pipeline Woodpecker

Dois workflows em `.woodpecker/`:

| Arquivo | Quando | O que faz |
|---------|--------|-----------|
| `ci.yml` | `push` e `pull_request` | Instala o backend, compila os módulos Python e gera um `.docx` de qualificação. No frontend, `npm ci`, `tsc --noEmit` e `npm run lint`. Sem secrets. |
| `deploy.yml` | `push` em `main` | Publica as imagens no GHCR com as tags `latest` e o SHA do commit, copia `deploy/docker-compose.prod.yml` para `/opt/padronizador-ppgsp` e faz `docker compose pull` e `up -d`. |

Imagens:

- `ghcr.io/leonardosilvacosta/padronizador-ppgsp-backend`
- `ghcr.io/leonardosilvacosta/padronizador-ppgsp-frontend`

O frontend é buildado com `NEXT_PUBLIC_API_URL=https://padronizador.leadcode.com.br`. O cliente já prefixa `/health` e `/api/v1`; o Nginx no mesmo host encaminha esses caminhos ao backend, então o navegador não cruza origem.

### Secrets no Woodpecker

Em **Settings > Secrets** do repositório:

| Secret | Conteúdo |
|--------|----------|
| `ghcr_user` | Usuário do GitHub (`LeonardoSilvaCosta`) |
| `ghcr_token` | PAT clássico com `write:packages` e `read:packages` |
| `vps_host` | IP ou hostname da VPS |
| `vps_ssh_port` | Porta SSH (padrão esperado: `2222`) |
| `vps_user` | Usuário com permissão de Docker |
| `vps_ssh_key` | Chave privada autorizada na VPS |

### Primeira vez na VPS

1. O passo `sync-compose` envia `deploy/docker-compose.prod.yml` para `/opt/padronizador-ppgsp` antes do `pull`. O diretório é criado no deploy.
2. Instale o virtual host a partir de `deploy/nginx.conf.example` (porta 80 com desafio ACME, 443 com `client_max_body_size 100M`). O Nginx fica fora do Compose.
3. Emita o certificado: `sudo certbot certonly --webroot -w /var/www/letsencrypt -d padronizador.leadcode.com.br` e recarregue o Nginx. Ajuste o método se o Certbot já estiver no plugin nginx.
4. Os containers escutam só em loopback: backend `127.0.0.1:8150`, frontend `127.0.0.1:3050`. Essas portas não ficam na interface pública. Na VPS atual as duas estão livres.

`deploy/.env.prod.example` documenta `CORS_ORIGINS` e a URL pública. Os valores equivalentes já estão no compose de produção.
