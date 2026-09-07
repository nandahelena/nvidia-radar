# Roteiro do vídeo — até 7 minutos

## 0:00–0:45 — Problema

Apresente o desafio: identificar startups brasileiras com maturidade em IA e indicar tecnologias NVIDIA relevantes, evitando recomendações genéricas ou alucinações.

## 0:45–2:00 — Arquitetura

Mostre `docs/graph.mmd` ou o diagrama do README. Explique Query Planner, Retriever, Classifier, RAG híbrido, Cohere Rerank, Recommender, Evidence Validator e Briefing Agent.

## 2:00–4:30 — Demonstração

Use a consulta de uma startup que desenvolve LLM próprio, preferencialmente Maritaca AI. Mostre a classificação, NVIDIA NeMo, a justificativa, a evidência com link e a exportação do briefing.

## 4:30–5:30 — Decisões técnicas

Explique embeddings locais, Qdrant, BM25, RRF, reranking e whitelist. Destaque que o caso da Writer aparece porque a busca é ampla antes do rerank.

## 5:30–6:20 — Segurança e limitações

Mostre o Evidence Validator, a tentativa única de recomposição e a transparência das fontes. Explique que respostas de LLM podem variar.

## 6:20–7:00 — Diferencial e encerramento

Mostre o risco de comoditização no briefing, exporte o resultado e encerre com o valor comercial do radar.
