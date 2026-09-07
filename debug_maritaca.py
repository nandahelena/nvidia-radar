import cohere
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
import os

load_dotenv()

co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

qdrant = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name="nvidia_knowledge"
)

query = "Startup fundada por pesquisadores da Unicamp que desenvolve LLMs próprios (família Sabiá) especializados em português brasileiro. Setor: Infraestrutura de IA. Classificação de maturidade em IA: AI-native."

# Passo 1: busca vetorial, trazendo um lote MAIOR de candidatos (top 10, não top 3)
candidatos = qdrant.similarity_search(query, k=30)

print("=== ANTES DO RERANK (ordem do Qdrant) ===")
for i, doc in enumerate(candidatos, 1):
    produto = doc.metadata.get('produto', '???')
    trecho = doc.page_content[:100].replace('\n', ' ')
    print(f"{i}. [{produto}] {trecho}...")

# Passo 2: reranking com Cohere
textos = [doc.page_content for doc in candidatos]

resultado_rerank = co.rerank(
    model="rerank-v3.5",
    query=query,
    documents=textos,
    top_n=10
)

print("\n=== DEPOIS DO RERANK (ordem refinada) ===")
for item in resultado_rerank.results:
    doc_original = candidatos[item.index]
    produto = doc_original.metadata.get('produto', '???')
    trecho = doc_original.page_content[:100].replace('\n', ' ')
    print(f"[score={item.relevance_score:.4f}] [{produto}] {trecho}...")