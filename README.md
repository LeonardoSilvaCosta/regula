# Regula

> **Motor de Conformidade e Estruturação de Documentos Acadêmicos**  
> *Da auditoria de regras à geração canônica de Relatórios de Qualificação, Dissertações e Teses.*

[![Production](https://img.shields.io/badge/Production-regula.leadcode.com.br-0f3d32?style=flat-square)](https://regula.leadcode.com.br)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16_App_Router-black?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-Woodpecker-orange?style=flat-square)](https://woodpecker-ci.org)
[![Docker](https://img.shields.io/badge/Deploy-Docker_Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)

---

## Visão Geral

O **Regula** é uma plataforma de engenharia documental e compliance normativo para a pós-graduação *stricto sensu*. Desenvolvido sob uma arquitetura desacoplada e escalável, o sistema audita manuscritos brutos, identifica inconformidades regulamentares e compila documentos canônicos em formato `.docx` (Microsoft Word) rigorosamente alinhados aos manuais institucionais e às normas ABNT/IBGE.

Projetado inicialmente como motor normativo do **Programa de Pós-Graduação em Segurança Pública da Universidade Federal do Pará (PPGSP/UFPA)**, sua arquitetura modular foi pensada para receber catálogos de regras de outros programas e áreas de avaliação.

### Resoluções Atendidas (Ruleset PPGSP/UFPA)

- **Resolução nº 007/2025:** Auditoria automática da Carteira de Produtos Técnicos e Tecnológicos (PTTs). Validação de cotas de impacto ($\ge 50\%$ Alto, $\le 25\%$ Médio, $\le 25\%$ Baixo, mínimo de 4 para mestrado e 8 para doutorado) e conformidade dos 22 campos da ficha técnica.
- **Resolução nº 009/2025:** Estruturação completa do Relatório de Qualificação com paginação romana preliminar, paginação arábica contínua no corpo textual, Quadro 1 da Apresentação em página paisagem, tabelas abertas no padrão IBGE/ABNT e campos dinâmicos `PAGEREF`.
- **Resolução nº 010/2025 (Revisão 2026):** Montagem canônica da Dissertação de Mestrado e Tese de Doutorado em 4 capítulos estruturados (Considerações Gerais, Artigos Científicos, Produtos Técnicos e Considerações Finais).

---

## Funcionalidades Principais

- **Wizard Interativo em 4 Passos:**
  1. **Upload & Seleção:** Leitura do `.docx` bruto com suporte a Mestrado e Doutorado.
  2. **Diagnóstico Normativo:** Painel visual com checklist de lacunas e barra métrica da carteira de PTTs.
  3. **Revisão de Metadados:** Edição antes da compilação (autor, banca examinadora, coorientador, siglas e produtos).
  4. **Compilação & Download:** Geração do `.docx` padronizado via streaming da API.
- **Engine OpenXML de Alta Fidelidade:** Construção de tabelas abertas IBGE, controle de quebras de seção contínuas e campos nativos do Word (`PAGE`, `PAGEREF`, `updateFields`).
- **Contrato de Dados Type-Safe:** Especificação OpenAPI gerada pela FastAPI e sincronizada automaticamente no frontend via `openapi-typescript`.
- **Pipeline de Entrega Contínua:** Integração com Woodpecker CI para validação de código, publicação de imagens imutáveis no GHCR e deploy automatizado na VPS.

---

## Arquitetura do Monorepo

```text
regula/
├── .woodpecker/                  # Workflows de CI e Deploy automatizado
│   ├── ci.yml                   # Gates de qualidade em push e pull_request
│   └── deploy.yml               # Buildx, GHCR e rollout na VPS (push na main)
├── backend/                      # API REST e Motor de Documentos (Python 3.11)
│   ├── app/
│   │   ├── api/v1/endpoints/    # Rotas FastAPI (/parse, /validate-ptts, /generate)
│   │   ├── schemas/             # Modelos Pydantic v2 (metadados, PTTs, bancas)
│   │   └── services/            # Serviços de parsing e compilação em memória
│   ├── core/                    # Estilos ABNT, paginação OpenXML e validador PTT
│   ├── generators/              # Construtores específicos (qualificação, dissertação, tese)
│   ├── assets/                  # Brasão institucional da UFPA
│   ├── Dockerfile               # Imagem slim de produção
│   └── main.py                  # CLI unificada (terminal local)
├── frontend/                     # Interface do Usuário (Next.js 16 + Tailwind CSS)
│   ├── src/
│   │   ├── app/                 # App Router e landing page
│   │   ├── components/wizard/   # Componentes do Stepper (Passos 1 a 4)
│   │   ├── lib/api.ts           # Cliente HTTP desacoplado
│   │   └── types/api.ts         # Tipos TypeScript sincronizados via OpenAPI
│   └── Dockerfile               # Build multi-stage standalone
├── deploy/                       # Artefatos de infraestrutura de produção
│   ├── docker-compose.prod.yml  # Compose de produção com imagens do GHCR
│   └── nginx.conf.example       # Virtual Host Nginx com proxy e SSL Let's Encrypt
├── docker-compose.yml            # Orquestração local de desenvolvimento
├── docker-compose.dev.yml        # Overlay de desenvolvimento com hot-reload
├── Makefile                      # Automação de tarefas locais (up, down, gen-types)
└── README.md
```

---

## Como Executar

### 1. Via Docker Compose (Recomendado)

Suba o backend (porta 8150) e o frontend (porta 3050) com um único comando:

```bash
docker compose up -d --build
```

Acesse no navegador: **`http://localhost:3050`** (ou `http://localhost:3000` em desenvolvimento).

### 2. Desenvolvimento Nativo

#### Backend (Terminal 1)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Swagger interativo disponível em: `http://localhost:8000/docs`

#### Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```

#### Sincronização de Tipos
Sempre que alterar schemas Pydantic no backend, sincronize os contratos no frontend com:
```bash
cd frontend
npm run gen:types
```

### 3. Modo CLI (Terminal)

O backend também funciona como utilitário de linha de comando:

```bash
cd backend
python main.py qualificacao -i inputs/qualificacao/projeto.docx -o outputs/qualificacao/Relatorio.docx -n mestrado
```

---

## Deploy e Produção

A aplicação de produção está hospedada na VPS sob o domínio **`https://regula.leadcode.com.br`**, operando atrás do Nginx com certificado SSL Let's Encrypt e os containers vinculados estritamente à interface de loopback (`127.0.0.1:8150` para API e `127.0.0.1:3050` para o Web):

- **Push na branch `main`:** O Woodpecker CI compila e publica as imagens no GitHub Container Registry (`ghcr.io/leonardosilvacosta/regula-*`), envia o compose via SCP e realiza o rollout na VPS com verificação de healthcheck em tempo real.

---

## Autor

Desenvolvido por **Leonardo Silva Costa**  
*Capitão QCOPM (Oficial Psicólogo) / Engenheiro de Software / Mestrando no PPGSP/UFPA*  
Belém, Pará, Brasil.
