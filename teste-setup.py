import os
from dotenv import load_dotenv
from groq import Groq
from qdrant_client import QdrantClient
import psycopg

# Carrega as variáveis do .env
load_dotenv()

print("=" * 50)
print("Testando configuração do ambiente")
print("=" * 50)

# Teste 1: Groq
try:
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    resposta = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": "Diga 'ok' em uma palavra"}]
    )
    print(f"✅ Groq funcionando: {resposta.choices[0].message.content}")
except Exception as e:
    print(f"❌ Erro no Groq: {e}")

# Teste 2: Qdrant
try:
    qdrant = QdrantClient(host="localhost", port=6333)
    collections = qdrant.get_collections()
    print(f"✅ Qdrant funcionando: {len(collections.collections)} coleções")
except Exception as e:
    print(f"❌ Erro no Qdrant: {e}")

# Teste 3: PostgreSQL
try:
    conn = psycopg.connect(
        host="localhost",
        port=5432,
        user="radar",
        password="radar123",
        dbname="startups"
    )
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        versao = cur.fetchone()[0]
    conn.close()
    print(f"✅ PostgreSQL funcionando: {versao[:50]}...")
except Exception as e:
    print(f"❌ Erro no PostgreSQL: {e}")

print("=" * 50)