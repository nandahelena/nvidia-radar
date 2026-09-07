import os
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


def carregar_documentos(pasta='data/nvidia'):
    """Lê os .txt e separa o texto do cabeçalho de metadados."""
    documentos = []
    for arquivo in Path(pasta).glob('*.txt'):
        conteudo = arquivo.read_text(encoding='utf-8')
        partes = conteudo.split('---\n', 1)
        cabecalho = partes[0]
        texto = partes[1] if len(partes) > 1 else conteudo
        
        # extrai metadados do cabeçalho (parsing simples)
        metadata = {}
        for linha in cabecalho.split('\n'):
            if ':' in linha:
                chave, valor = linha.split(':', 1)
                metadata[chave.strip().lower()] = valor.strip()
        
        documentos.append(Document(page_content=texto, metadata=metadata))
    return documentos


def main():
    print("Carregando documentos...")
    documentos = carregar_documentos()
    print(f"  {len(documentos)} documentos carregados")
    
    print("Fazendo chunking...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documentos)
    print(f"  {len(chunks)} chunks gerados")
    
    print("Carregando modelo de embeddings (primeira vez baixa ~80MB)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    print("Conectando ao Qdrant e indexando...")
    qdrant = QdrantVectorStore.from_documents(
        chunks,
        embedding=embeddings,
        url="http://localhost:6333",
        collection_name="nvidia_knowledge"
    )
    
    print(f"\nConcluído! {len(chunks)} chunks indexados na coleção 'nvidia_knowledge'")


if __name__ == "__main__":
    main()