# Avaliação de qualidade

## Conjunto mínimo

| Consulta | Evidência esperada | Verificação |
|---|---|---|
| Startup que desenvolve LLM próprio | NVIDIA NeMo / NeMo Framework | O case da Writer deve aparecer entre os candidatos reranqueados |
| Deploy de LLM com baixa latência | NVIDIA NIM ou TensorRT-LLM | O produto deve aparecer com fonte oficial |
| Aplicação de voz em português | NVIDIA Riva | Os chunks de ASR/TTS devem ser recuperados |

## Procedimento

1. Executar a consulta na interface.
2. Conferir no log a query, os 30 candidatos e os 4 trechos finais.
3. Conferir se cada recomendação exibe `Evidências usadas` com URL.
4. Repetir uma consulta com produto inválido simulado para verificar o alerta do Evidence Validator.
5. Exportar o briefing e abrir o `.md` gerado.

## Resultado conhecido

Para a Maritaca AI, a busca híbrida recupera 359 chunks no índice local, mantém o case da Writer entre os candidatos e o Cohere o posiciona em primeiro lugar (`0.1715` na execução validada). O agente completo recomendou NVIDIA NeMo com prioridade alta.
