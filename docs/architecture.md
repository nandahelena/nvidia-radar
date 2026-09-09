# Arquitetura

## Visão geral

O NVIDIA Startup AI Radar separa a descoberta de startups da busca de conhecimento NVIDIA. Essa separação permite classificar o contexto do negócio antes de recomendar tecnologias e manter as recomendações vinculadas a fontes recuperadas.

O fluxo completo está em [graph.mmd](graph.mmd). Há seis agentes LangGraph:

| Agente | Responsabilidade | Entrada principal | Saída principal |
| --- | --- | --- | --- |
| Query Planner | Extrai intenção, setor e filtros da pergunta | Consulta textual | Critérios de busca |
| Retriever | Consulta startups e documentos no PostgreSQL | Critérios estruturados | Startups e fontes do negócio |
| Classifier | Classifica o papel da IA no produto | Perfil e documentos da startup | AI-native, AI-enabled ou non-AI |
| Recommender | Conecta necessidade técnica a produtos NVIDIA | Classificação e evidências | Recomendações estruturadas |
| Evidence Validator | Impede produtos e fontes não suportados | Recomendações e whitelist | Alertas ou recomendações aprovadas |
| Briefing Agent | Sintetiza a resposta para uso comercial | Estado validado | Briefing e exportação |

## Camadas de dados

### PostgreSQL

Armazena as startups e os documentos associados carregados de `data/startups/*.json`. A variável `DATABASE_URL` define a conexão. O schema está em `database/schema.sql`.

### Qdrant

Armazena os vetores dos documentos NVIDIA. A indexação lê `data/nvidia/*.txt`, separa os metadados, cria chunks de 500 caracteres com sobreposição de 50 e usa `all-MiniLM-L6-v2` para embeddings.

### Recuperação híbrida

O retriever combina duas estratégias:

1. busca vetorial no Qdrant;
2. busca lexical BM25 sobre os mesmos chunks.

Os rankings são combinados com Reciprocal Rank Fusion. Os candidatos resultantes seguem para Cohere Rerank, que reduz o conjunto antes da geração da recomendação.

## Controle de evidências

As recomendações estruturadas carregam tecnologia, justificativas, prioridade, complexidade, próxima ação e evidências. O Evidence Validator compara os produtos contra a whitelist e mantém apenas URLs presentes nos documentos recuperados.

Quando há alerta, o grafo retorna ao Recommender uma única vez. Se a segunda validação falhar, o fluxo segue para o briefing com o alerta explícito, evitando um loop infinito.

## Decisões e limites

- O Classifier absorve a antiga etapa de extração para evitar uma chamada adicional ao LLM.
- O PostgreSQL é usado para relações e filtros de startup; o Qdrant é reservado ao conhecimento documental.
- O modelo e os provedores são configurados por variáveis de ambiente.
- A arquitetura atual é local: não há autenticação, observabilidade distribuída ou configuração de produção.
