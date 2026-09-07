from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

client.delete_collection(collection_name="nvidia_knowledge")
print("Coleção 'nvidia_knowledge' removida. Pronta para reindexação.")