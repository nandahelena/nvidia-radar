"""Busca híbrida: recuperação vetorial + BM25 com fusão por RRF."""

import re
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi


def _tokens(texto):
    return re.findall(r"\w+", texto.lower(), flags=re.UNICODE)


def _carregar_chunks():
    pasta = Path(__file__).resolve().parents[2] / "data" / "nvidia"
    documentos = []
    for arquivo in sorted(pasta.glob("*.txt")):
        conteudo = arquivo.read_text(encoding="utf-8")
        cabecalho, separador, texto = conteudo.partition("---\n")
        metadata = {"arquivo": arquivo.name}
        for linha in cabecalho.splitlines():
            if ":" in linha:
                chave, valor = linha.split(":", 1)
                metadata[chave.strip().lower()] = valor.strip()
        documentos.append(Document(page_content=texto if separador else conteudo, metadata=metadata))

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_documents(documentos)


_CHUNKS = _carregar_chunks()
_BM25 = BM25Okapi([_tokens(doc.page_content) for doc in _CHUNKS])


def buscar_candidatos_hibridos(qdrant, query, k=30):
    """Combina ranking vetorial e lexical antes do rerank semântico do Cohere."""
    vetoriais = qdrant.similarity_search(query, k=k)
    scores_bm25 = _BM25.get_scores(_tokens(query))
    indices_lexicais = sorted(range(len(scores_bm25)), key=scores_bm25.__getitem__, reverse=True)[:k]

    # Reciprocal Rank Fusion: reduz a dependência de uma única estratégia.
    fusao = {}
    documentos = {}
    for ranking in (vetoriais, [_CHUNKS[i] for i in indices_lexicais]):
        for posicao, doc in enumerate(ranking, start=1):
            chave = (doc.metadata.get("produto"), doc.page_content)
            documentos[chave] = doc
            fusao[chave] = fusao.get(chave, 0.0) + 1.0 / (60 + posicao)

    ordenados = sorted(fusao, key=fusao.get, reverse=True)
    return [documentos[chave] for chave in ordenados[:k]]
