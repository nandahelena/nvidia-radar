from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=os.getenv("GROQ_API_KEY")
)

PROMPT_TEMPLATE = """
Você é um planejador de consultas especializado em startups. 
Sua tarefa é analisar a consulta do usuário em linguagem natural e extrair critérios de busca estruturados.

### Regras de Extração:
- setor: A vertical ou área de atuação da startup (ex: saúde, fintech, jurídico). Use null se não mencionado.
- estagio: A fase de investimento ou maturidade (ex: seed, série A, unicórnio). Use null se não mencionado.
- classificacao_ia: Deve ser estritamente "AI-native", "AI-enabled", "non-AI", ou null se não mencionado.
- palavras_chave: Um array (lista) contendo os principais termos relevantes da consulta.

### Restrições:
Responda ESTRITAMENTE com um objeto JSON válido. 
Não inclua nenhum texto antes ou depois, e não use blocos de formatação markdown (```json).

### Exemplo de Saída Esperada:
{{
  "setor": "fintech",
  "estagio": "série A",
  "classificacao_ia": "AI-enabled",
  "palavras_chave": ["pagamentos", "B2B", "crédito"]
}}

Consulta do usuário: {consulta}
"""


def query_planner_agent(state):
    consulta = state["consulta"]

    prompt = PROMPT_TEMPLATE.format(consulta=consulta)
    resposta = llm.invoke(prompt)

    texto = resposta.content.strip()

    # 1. Remove os marcadores markdown de bloco de código (```json e ```)
    # A regex procura por "```json", "```JSON" ou apenas "```" e substitui por nada
    texto_limpo = re.sub(r"```(?:json)?", "", texto, flags=re.IGNORECASE).strip()

    # 2 e 3. Transforma a string em dict com tratamento de erro (fallback)
    try:
        criterios = json.loads(texto_limpo)
    except json.JSONDecodeError:
        # Fallback seguro para não quebrar o pipeline
        criterios = {
            "setor": None,
            "estagio": None,
            "classificacao_ia": None,
            "palavras_chave": []
        }

    return {"criterios_busca": criterios}

if __name__ == "__main__":
    state = {"consulta": "startups de saúde usando IA", "criterios_busca": {}, "startups_encontradas": [], "classificacoes": {}, "recomendacoes": {}}
    resultado = query_planner_agent(state)
    print(resultado)