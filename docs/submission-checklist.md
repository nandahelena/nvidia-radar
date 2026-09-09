# Checklist de entrega

## Código e arquitetura

- [x] LangGraph com Query Planner, Retriever, Classifier, Recommender, Evidence Validator e Briefing Agent.
- [x] Transição condicional de retry após falha de validação.
- [x] Extractor documentado como responsabilidade absorvida pelo Classifier.
- [x] Diagrama em `docs/graph.mmd` e Mermaid no README.
- [x] Saída estruturada Pydantic com fallback textual.

## RAG e evidências

- [x] Qdrant com embeddings locais.
- [x] BM25 + busca vetorial + RRF + Cohere Rerank.
- [x] 359 chunks carregados no índice lexical.
- [x] Evidências NVIDIA com produto e URL.
- [x] URLs dos documentos da startup preservadas para a classificação.
- [x] Casos de avaliação, critérios e procedimento registrados em `docs/evaluation.md`.

## Interface

- [x] Cards de recomendação e classificação.
- [x] Alertas do Evidence Validator visíveis.
- [x] Mensagem para zero resultados.
- [x] Mensagem específica para limite de quota do provedor.
- [x] Exportação do briefing em Markdown.

## Qualidade

- [x] Seis testes automatizados passando no ambiente virtual.
- [x] Sintaxe Python validada.
- [x] `git diff --check` sem erros na última validação registrada.
- [ ] Executar a demo completa com as chaves ativas e registrar o resultado em `docs/evaluation.md`.
- [ ] Validar visualmente a interface na versão final.

## Antes de publicar

- [ ] Demonstrar uma recomendação com evidência e exportação.
- [ ] Conferir se `.env` e credenciais não estão no commit.
- [ ] Conferir prazo e publicar o repositório.
