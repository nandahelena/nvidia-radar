# NVIDIA Startup AI Radar

<p align="center">
  <img src="assets/nvidia-radar-logo.svg" alt="Logo do NVIDIA Startup AI Radar" width="180">
</p>

<p align="center">
  <strong>Inteligência para descobrir a maturidade em IA de startups brasileiras e recomendar tecnologias NVIDIA.</strong>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10 ou superior"></a>
  <a href="https://streamlit.io/"><img src="https://img.shields.io/badge/Interface-Streamlit-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit"></a>
  <a href="https://www.langchain.com/langgraph"><img src="https://img.shields.io/badge/Orquestração-LangGraph-1C3C3C" alt="LangGraph"></a>
  <a href="https://qdrant.tech/"><img src="https://img.shields.io/badge/Vetores-Qdrant-DC244C" alt="Qdrant"></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Infra-Docker-2496ED?logo=docker&logoColor=white" alt="Docker"></a>
</p>

O **NVIDIA Startup AI Radar** é uma aplicação multiagente que transforma uma pergunta sobre startups em um briefing comercial fundamentado. O sistema encontra empresas na base local, classifica o papel da IA no produto e cruza cada caso com a documentação oficial da NVIDIA para sugerir tecnologias, prioridades, complexidade e evidências.

## O que a aplicação faz

- interpreta consultas em linguagem natural, como `startups de saúde usando IA`;
- recupera startups e documentos estruturados no PostgreSQL;
- classifica cada produto como `AI-native`, `AI-enabled` ou `non-AI`;
- busca documentação NVIDIA com recuperação híbrida: vetorial, BM25 e Reciprocal Rank Fusion;
- aplica Cohere Rerank para selecionar os trechos mais relevantes;
- recomenda tecnologias NVIDIA com justificativas técnicas e de negócio;
- valida produtos e URLs citados antes de montar o briefing final;
- apresenta resultados, métricas, evidências e exportação na interface Streamlit.

## Arquitetura

```mermaid
flowchart LR
    A[Consulta] --> B[Query Planner]
    B --> C[Retriever PostgreSQL]
    C --> D[Classifier]
    D --> E[Retriever NVIDIA]
    E --> F[BM25 + vetorial + RRF]
    F --> G[Cohere Rerank]
    G --> H[Recommender]
    H --> I[Evidence Validator]
    I -->|uma tentativa de correção| H
    I --> J[Briefing Agent]
    J --> K[Streamlit / exportação]
```

O fluxo é orquestrado com LangGraph. O Qdrant mantém os embeddings dos documentos NVIDIA; o PostgreSQL mantém startups e documentos de contexto. O modelo de linguagem é fornecido pelo Groq.

## Pré-requisitos

- Python 3.10 ou superior;
- Docker Desktop em execução;
- uma chave `GROQ_API_KEY`;
- uma chave `COHERE_API_KEY` para o reranking;
- Git, caso o projeto seja clonado.

## Instalação

Clone o projeto e entre na pasta:

```bash
git clone <URL_DO_REPOSITORIO>
cd nvidia-radar
```

Crie e ative um ambiente virtual. No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

No Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configuração

Crie um arquivo `.env` na raiz do projeto. O arquivo é ignorado pelo Git para não expor chaves:

```dotenv
DATABASE_URL=postgresql://radar:radar123@localhost:5432/startups
GROQ_API_KEY=sua-chave-groq
GROQ_MODEL=openai/gpt-oss-20b
COHERE_API_KEY=sua-chave-cohere
LLM_TIMEOUT=90
LLM_MAX_RETRIES=1
```

`GROQ_MODEL`, `LLM_TIMEOUT` e `LLM_MAX_RETRIES` são opcionais. Se `GROQ_MODEL` não for informado, o projeto usa `openai/gpt-oss-20b`.

## Como executar

### 1. Inicie os serviços de infraestrutura

O `docker-compose.yml` inicia PostgreSQL na porta `5432` e Qdrant na porta `6333`:

```bash
docker compose up -d
docker compose ps
```

### 2. Crie o schema do PostgreSQL

Execute uma vez após subir o banco:

```bash
python database/init_db.py
```

### 3. Popule a base de startups

Os arquivos JSON em `data/startups/` são carregados no PostgreSQL. O script limpa os registros existentes antes de inserir a base novamente:

```bash
python database/populate_db.py
```

### 4. Indexe a documentação NVIDIA no Qdrant

Esse passo lê os arquivos em `data/nvidia/`, cria chunks e baixa o modelo de embeddings na primeira execução:

```bash
python src/rag/index_nvidia.py
```

### 5. Inicie a aplicação

```bash
streamlit run app.py
```

Abra `http://localhost:8501` no navegador. Em Windows, também é possível executar diretamente com:

```powershell
\.venv\Scripts\streamlit.exe run app.py
```

## Testes e verificações

Execute os testes automatizados:

```bash
python -m unittest discover -s tests -v
```

Para verificar a recuperação no Qdrant depois da indexação:

```bash
python src/rag/test_retrieval.py
```

Para investigar manualmente candidatos e reranking da Maritaca AI:

```bash
python debug_maritaca.py
```

## Scripts úteis

| Arquivo | Finalidade |
| --- | --- |
| `app.py` | Interface Streamlit e entrada do usuário |
| `database/init_db.py` | Criação das tabelas do PostgreSQL |
| `database/populate_db.py` | Carga dos JSONs de startups e documentos |
| `src/rag/index_nvidia.py` | Chunking, embeddings e indexação no Qdrant |
| `src/rag/test_retrieval.py` | Smoke test da coleção vetorial |
| `clear_qdrant.py` | Remove a coleção local para uma reindexação limpa |
| `docs/evaluation.md` | Casos de avaliação e resultados esperados |
| `docs/video-script.md` | Roteiro de demonstração do projeto |

## Solução de problemas

**O PostgreSQL ou Qdrant não conecta**

Confirme que os containers estão ativos com `docker compose ps`. Se necessário, veja os logs com `docker compose logs postgres` ou `docker compose logs qdrant`.

**A coleção `nvidia_knowledge` não existe**

Execute `python src/rag/index_nvidia.py`. A primeira execução pode baixar o modelo `all-MiniLM-L6-v2`.

**A aplicação informa erro de quota ou HTTP 429**

O limite do provedor Groq foi atingido. Aguarde a renovação da quota ou configure outra chave/modelo no `.env`.

**O banco precisa ser recriado**

Para remover também os volumes persistentes e começar de novo, use o comando destrutivo abaixo conscientemente:

```bash
docker compose down -v
docker compose up -d
python database/init_db.py
python database/populate_db.py
python src/rag/index_nvidia.py
```

## Limitações conhecidas

- classificações e textos gerados dependem do modelo de linguagem e podem variar entre execuções;
- o score de risco de comoditização é uma heurística explicável, não uma previsão financeira;
- o Evidence Validator usa uma whitelist de produtos NVIDIA e permite no máximo uma tentativa de recomposição;
- PostgreSQL e Qdrant são executados localmente e não têm configuração de produção neste repositório.

## Documentação adicional

- [Avaliação](docs/evaluation.md)
- [Grafo da solução](docs/graph.mmd)
- [Checklist de entrega](docs/submission-checklist.md)
- [Roteiro do vídeo](docs/video-script.md)

## Licença

Este repositório não declara uma licença de distribuição. Consulte os responsáveis pelo projeto antes de reutilizar ou redistribuir o código.
