# Avaliação de qualidade

Este documento define como verificar o comportamento do radar sem depender apenas de uma resposta visualmente plausível. A avaliação cobre recuperação, recomendação, evidências, validação e exportação.

## Pré-condições

1. Subir PostgreSQL e Qdrant com `docker compose up -d`.
2. Criar e popular o PostgreSQL com `database/init_db.py` e `database/populate_db.py`.
3. Criar a coleção `nvidia_knowledge` com `src/rag/index_nvidia.py`.
4. Configurar `GROQ_API_KEY` e `COHERE_API_KEY` no `.env`.
5. Executar `python -m unittest discover -s tests -v`.

O índice lexical atual possui 359 chunks derivados dos documentos em `data/nvidia/`. Os resultados podem mudar quando os documentos, o modelo ou as quotas dos provedores mudarem.

## Casos funcionais

| ID | Consulta | Comportamento esperado | Evidência de aprovação |
| --- | --- | --- | --- |
| EVAL-01 | `startups de saúde usando IA` | Encontra startups do setor e classifica os produtos | Há resultados e uma classificação para cada startup |
| EVAL-02 | `startups AI-native` | Prioriza produtos cuja IA é parte central da proposta | Pelo menos um resultado `AI-native` aparece quando disponível |
| EVAL-03 | `startup que desenvolve LLM próprio` | Recupera documentação de NeMo ou NeMo Framework | A recomendação contém o produto e uma URL NVIDIA |
| EVAL-04 | `deploy de LLM com baixa latência` | Recupera NIM ou tecnologia relacionada | A recomendação explica o encaixe técnico e cita fonte |
| EVAL-05 | `aplicação de voz em português` | Recupera documentação de ASR/TTS do Riva | NVIDIA Riva aparece entre as evidências relevantes |
| EVAL-06 | Consulta sem correspondência | Não quebra a interface | Exibe mensagem de zero resultados sem chamar a etapa de briefing |
| EVAL-07 | Recomendação com produto inválido | Bloqueia produto fora da whitelist | `Evidence Validator` registra alerta e tenta recompor uma vez |
| EVAL-08 | Exportação de briefing | Preserva síntese e evidências | O Markdown exportado abre e contém URLs permitidas |
| EVAL-09 | Score de comoditização | Prioriza o risco competitivo por startup | O briefing exportado contém `Risco de comoditização: alto`, `médio` ou `baixo` para cada startup |

## Critérios de qualidade

Uma execução é aprovada quando:

- a aplicação conclui sem exceção não tratada;
- o resultado mostra a classificação e o racional para as startups encontradas;
- cada recomendação NVIDIA possui tecnologia, justificativa e pelo menos uma fonte recuperada;
- URLs inventadas ou fora das evidências recuperadas não aparecem na saída final;
- a validação respeita o limite de uma recomposição;
- a exportação produz Markdown legível;
- uma consulta sem resultados recebe uma resposta explícita e útil.
- cada startup do briefing exportado recebe um score de risco de comoditização.

## Procedimento manual

1. Inicie a aplicação com `streamlit run app.py`.
2. Execute EVAL-01, EVAL-03, EVAL-04 e EVAL-05 na interface.
3. Para cada resposta, registre consulta, startups encontradas, classificação, tecnologias, URLs e eventuais alertas.
4. Execute EVAL-06 com uma consulta deliberadamente inexistente.
5. Use os testes automatizados para cobrir EVAL-07 e a filtragem de fontes.
6. Exporte o briefing de EVAL-03 e valide o arquivo Markdown.
7. Confirme em EVAL-09 que o risco aparece junto da classificação de cada startup.

## Resultados registrados

Na execução de referência com `k=30` e Cohere `top_n=5`:

- LLM próprio em português recuperou `NVIDIA NeMo` em primeiro lugar.
- Deploy de LLM com baixa latência recuperou `NVIDIA NIM` em primeiro lugar.
- Voz com ASR/TTS recuperou `NVIDIA Riva` entre os primeiros resultados.
- Para Maritaca AI, a busca híbrida manteve o caso da Writer entre os candidatos e o reranker o posicionou em primeiro lugar, com recomendação de NVIDIA NeMo em prioridade alta.

Esses resultados são uma referência funcional, não um snapshot imutável. Para uma comparação histórica, registre data, modelo, quantidade de chunks, parâmetros de recuperação e versão dos documentos.

## Matriz de rastreabilidade

| Área | Implementação | Verificação |
| --- | --- | --- |
| Orquestração | `src/graph.py` | `tests/test_pipeline.py` |
| Classificação | `src/agents/classifier_agent.py` | EVAL-01 e EVAL-02 |
| Recuperação | `src/rag/hybrid_retriever.py` e `src/agents/recommender_agent.py` | EVAL-03 a EVAL-05 |
| Validação | `src/agents/evidence_validator_agent.py` | EVAL-07 |
| Interface | `app.py` | EVAL-06 e EVAL-08 |
| Priorização estratégica | `src/agents/briefing_agent.py` | EVAL-09 |
