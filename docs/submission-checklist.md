# Checklist final de entrega — TAPI

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
- [x] Casos de avaliação registrados em `docs/evaluation.md`.

## Interface

- [x] Cards de recomendação e classificação.
- [x] Alertas do Evidence Validator visíveis.
- [x] Mensagem para zero resultados.
- [x] Mensagem específica para limite de quota do provedor.
- [x] Exportação do briefing em Markdown.

## Qualidade

- [x] Seis testes automatizados passando.
- [x] Sintaxe Python validada.
- [x] `git diff --check` sem erros.
- [x] Interface Streamlit carregada visualmente.
- [ ] Executar a demo completa depois da renovação da quota Groq.

## Entrega manual

- [ ] Gravar o vídeo de até 7 minutos usando `docs/video-script.md`.
- [ ] Demonstrar uma recomendação com evidência e exportação.
- [ ] Conferir prazo e enviar o repositório/vídeo.
