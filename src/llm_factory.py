"""Cria o modelo Groq usado pelos agentes."""

import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv(override=True)


def create_llm():
    """Retorna o único LLM usado no fluxo de produção do projeto."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Groq exige GROQ_API_KEY no arquivo .env.")

    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        api_key=api_key,
        timeout=float(os.getenv("LLM_TIMEOUT", "90")),
        max_retries=int(os.getenv("LLM_MAX_RETRIES", "1")),
    )
