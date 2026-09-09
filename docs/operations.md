# Operação e manutenção

## Inicialização normal

```bash
docker compose up -d
python database/init_db.py
python database/populate_db.py
python src/rag/index_nvidia.py
streamlit run app.py
```

Depois da primeira carga, `init_db.py`, `populate_db.py` e `index_nvidia.py` só precisam ser repetidos quando o schema, os dados ou os documentos forem alterados.

## Verificações rápidas

```bash
docker compose ps
python -m unittest discover -s tests -v
python src/rag/test_retrieval.py
```

O endpoint local do Qdrant também pode ser consultado em `http://localhost:6333`. A aplicação Streamlit fica em `http://localhost:8501` por padrão.

## Atualização dos dados

Para atualizar startups, edite os JSONs em `data/startups/` e execute novamente `python database/populate_db.py`. O script faz `TRUNCATE` das tabelas antes da carga, portanto a operação substitui a base inteira.

Para atualizar os documentos NVIDIA, edite `data/nvidia/` e reindexe. Se a coleção antiga precisar ser removida primeiro:

```bash
python clear_qdrant.py
python src/rag/index_nvidia.py
```

## Diagnóstico

| Sintoma | Verificação | Ação |
| --- | --- | --- |
| Falha de conexão com banco | `docker compose ps` e `DATABASE_URL` | Subir PostgreSQL e conferir credenciais |
| Coleção ausente | `python src/rag/test_retrieval.py` | Executar a indexação NVIDIA |
| HTTP 429 | Mensagem da interface e quota do provedor | Aguardar quota ou trocar chave/modelo |
| Nenhuma startup | Consulta e conteúdo de `data/startups/` | Recarregar a base e ampliar a consulta |
| Fonte não aparece | Documentos recuperados e whitelist | Conferir URL e reexecutar a busca |

## Desligamento e limpeza

Para parar os serviços sem apagar os dados:

```bash
docker compose stop
```

Para remover containers e volumes, apagando o banco e a coleção local:

```bash
docker compose down -v
```

Use a segunda opção apenas quando quiser reconstruir o ambiente do zero.
