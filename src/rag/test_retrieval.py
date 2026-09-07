from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore


def main():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    qdrant = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        url="http://localhost:6333",
        collection_name="nvidia_knowledge"
    )
    
    perguntas = [
        "como fazer deploy de LLM em produção com baixa latência?",
        "quais os benefícios do programa para startups?",
        "como transformar áudio em texto?",
    ]
    
    for pergunta in perguntas:
        print(f"\n=== {pergunta} ===")
        resultados = qdrant.similarity_search(pergunta, k=3)
        for i, doc in enumerate(resultados, 1):
            produto = doc.metadata.get('produto', '???')
            trecho = doc.page_content[:150].replace('\n', ' ')
            print(f"{i}. [{produto}] {trecho}...")


if __name__ == "__main__":
    main()