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

## Deploy na VPS

1. Clone o repositório na VPS e defina a URL pública da API antes do build, por exemplo `NEXT_PUBLIC_API_URL=https://api.seudominio.edu.br`.
2. Suba os serviços: `docker compose up --build -d`. Eles escutam em `127.0.0.1` se você ajustar o mapeamento para `127.0.0.1:3000:3000` e `127.0.0.1:8000:8000`, ou permanecem em `3000` e `8000` atrás do Nginx.
3. Aponte dois server blocks (ou um site e um subdomínio) para esses upstreams e emita o certificado com Certbot.

Exemplo de proxy (site na 3000, API na 8000):

```nginx
server {
    server_name padronizador.seudominio.edu.br;
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    server_name api.seudominio.edu.br;
    client_max_body_size 32m;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Certificados:

```bash
sudo certbot --nginx -d padronizador.seudominio.edu.br -d api.seudominio.edu.br
```

A API aceita `http://localhost:3000` e `http://127.0.0.1:3000`. Se o navegador chamar a API a partir de outro host, defina `CORS_ORIGINS` (origens separadas por vírgula) no `docker compose` e suba de novo.
