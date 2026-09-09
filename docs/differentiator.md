# Diferencial estratégico

## A pergunta além da recomendação

Uma ferramenta de recomendação convencional responde: **qual produto NVIDIA combina com esta startup?**

O NVIDIA Startup AI Radar acrescenta uma segunda pergunta: **qual é o risco de essa startup ser absorvida por uma funcionalidade nativa de um grande laboratório de IA?**

Essa camada é importante porque uma startup pode usar IA sem ter uma defesa competitiva forte. Um produto que apenas conecta uma API de LLM a uma interface, sem dados proprietários, workflow profundo ou especialização difícil de replicar, pode ser pressionado por uma feature nativa da OpenAI, Google ou Anthropic.

O radar transforma essa hipótese em um sinal de priorização no briefing executivo. Assim, a NVIDIA pode analisar não apenas o uso atual de IA, mas também onde existe uma oportunidade de nutrir uma startup com infraestrutura, software, conhecimento técnico e diferenciação.

## Como o score funciona

O cálculo está em `src/agents/briefing_agent.py`, na função `score_risco_commoditizacao`. Ele é determinístico e não faz uma chamada adicional ao modelo.

| Regra | Resultado |
| --- | --- |
| A startup é `AI-native` ou contém pelo menos três sinais de IA na descrição | `alto` |
| A startup é `AI-enabled` ou contém pelo menos um sinal de IA na descrição | `médio` |
| Nenhuma das regras anteriores é satisfeita | `baixo` |

Os sinais textuais atuais são:

- `llm`;
- `modelo`;
- `inteligência artificial`;
- `ia`;
- `chatbot`;
- `automação`.

## Como interpretar

O score não significa que uma empresa será substituída. Ele é um **indicador de triagem**:

- **Alto:** investigar rapidamente se a startup possui dados, distribuição, workflow ou tecnologia proprietária que compensem a dependência de capacidades genéricas.
- **Médio:** há uso relevante de IA, mas a diferenciação precisa ser entendida antes de priorizar investimento ou parceria.
- **Baixo:** a descrição não apresenta sinais suficientes de exposição a capacidades genéricas de IA; isso não elimina outros riscos competitivos.

O resultado deve ser lido junto da classificação `AI-native`, `AI-enabled` ou `non-AI`, das fontes da startup e das recomendações NVIDIA. O score isolado não deve orientar uma decisão de investimento.

## Por que isso diferencia o case

A base de startups pode ser igual para diferentes entregas. O diferencial está na camada de decisão construída sobre essa base:

1. identifica o papel da IA no produto;
2. recomenda uma tecnologia NVIDIA sustentada por evidências;
3. aponta o risco de comoditização que pode afetar a startup;
4. transforma o resultado em uma hipótese de priorização comercial.

Isso conecta a análise técnica à pergunta estratégica do case: **como a NVIDIA pode identificar e nutrir startups AI-native em um mercado em que capacidades de IA tendem a se tornar nativas das grandes plataformas?**

## Limitações atuais

- O score usa descrição textual e classificação; não verifica dados proprietários, retenção, distribuição, margem ou profundidade do workflow.
- Os rótulos `alto`, `médio` e `baixo` são relativos à heurística atual, não probabilidades calibradas.
- O score é incluído no briefing Markdown exportado. A interface Streamlit exibe a classificação e as recomendações nos cards, mas ainda não mostra esse risco como métrica separada na tela.
- Uma evolução natural seria decompor o score em fatores explicáveis, como dados proprietários, switching cost, distribuição, workflow e dependência de API.