import cohere
import logging
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
import os
from rag.hybrid_retriever import buscar_candidatos_hibridos

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=os.getenv("GROQ_API_KEY")
)

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

qdrant = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name="nvidia_knowledge"
)

co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))

logger = logging.getLogger(__name__)


def buscar_documentos_relevantes(query, k_inicial=30, top_n_final=4):
    """
    Busca candidatos no Qdrant (busca ampla) e refina com Cohere Rerank
    (busca precisa), retornando só os trechos mais relevantes.
    """
    candidatos = buscar_candidatos_hibridos(qdrant, query, k=k_inicial)

    logger.info(
        "Busca NVIDIA: %d candidatos recuperados para a query: %s",
        len(candidatos),
        query,
    )

    textos = [doc.page_content for doc in candidatos]

    resultado_rerank = co.rerank(
        model="rerank-v3.5",
        query=query,
        documents=textos,
        top_n=top_n_final
    )

    documentos_refinados = []
    for item in resultado_rerank.results:
        doc_original = candidatos[item.index]
        documentos_refinados.append(doc_original)
        logger.info(
            "Trecho enviado ao prompt: score=%.4f produto=%s preview=%s",
            item.relevance_score,
            doc_original.metadata.get("produto", "???"),
            doc_original.page_content[:160].replace("\n", " "),
        )

    return documentos_refinados


def buscar_trechos_relevantes(query, k_inicial=30, top_n_final=4):
    """Compatibilidade: retorna apenas o texto dos documentos reranqueados."""
    return [
        doc.page_content
        for doc in buscar_documentos_relevantes(query, k_inicial, top_n_final)
    ]



PROMPT_TEMPLATE = """
Você é um especialista técnico da NVIDIA responsável por identificar
tecnologias do catálogo NVIDIA que possam gerar valor para uma startup.

Sua tarefa é analisar o perfil da startup e os trechos recuperados da
documentação NVIDIA e recomendar as tecnologias mais relevantes.

PERFIL DA STARTUP

Nome: {nome}
Setor: {setor}
Descrição: {descricao_curta}
Classificação de maturidade em IA: {classificacao}


DOCUMENTAÇÃO NVIDIA RECUPERADA

{trechos_nvidia}


REGRAS DE RECOMENDAÇÃO

1. Recomende somente tecnologias que estejam claramente relacionadas aos
   trechos da documentação NVIDIA fornecidos.

2. Não invente tecnologias, funcionalidades, integrações ou benefícios que
   não estejam sustentados pelas informações fornecidas.

3. Considere a classificação de maturidade em IA da startup:
   - AI-native: priorize tecnologias diretamente relacionadas à construção,
     treinamento, inferência ou operação de soluções baseadas em IA.
   - AI-enabled: priorize tecnologias que possam melhorar ou ampliar as
     funcionalidades de IA existentes.
   - non-AI: priorize tecnologias que possam representar uma porta de entrada
     para aplicações de IA relevantes ao negócio, mas não presuma que a
     startup já utiliza IA.

4. Considere também o setor e o problema de negócio da startup. Uma tecnologia
   tecnicamente relacionada, mas sem aplicação clara para o negócio, não deve
   ser recomendada.

5. Prefira recomendações específicas e acionáveis em vez de recomendações
   genéricas.

6. Recomende no máximo 2 tecnologias. Se apenas uma tecnologia for claramente
   adequada, recomende somente uma.

7. Se os trechos recuperados não fornecerem evidências suficientes para uma
   recomendação confiável, não invente uma resposta. Nesse caso, informe que
   não foi possível identificar uma recomendação suficientemente fundamentada.


FORMATO DA RESPOSTA

Para cada tecnologia recomendada, use exatamente esta estrutura:

Tecnologia: [nome da tecnologia NVIDIA]

Justificativa técnica: [explique por que a tecnologia é tecnicamente
adequada para o perfil da startup, usando as informações recuperadas]

Justificativa de negócio: [explique qual problema ou oportunidade de negócio
a tecnologia pode ajudar a resolver]

Prioridade: [alta, média ou baixa]

Complexidade de implementação: [alta, média ou baixa]

Próxima ação sugerida: [indique uma ação prática que o time NVIDIA poderia
tomar para avaliar ou iniciar a adoção da tecnologia]

Evidências usadas: [liste o produto NVIDIA e o link da fonte que sustentam
esta recomendação]

Não inclua tecnologias que não possam ser justificadas pelos trechos
fornecidos.

Use somente os links presentes nos trechos recuperados e inclua essa seção
para cada tecnologia recomendada.
"""


def recommender_agent(state):
    recomendacoes = {}
    evidencias = {}

    for startup in state["startups_encontradas"]:
        nome = startup["nome"]
        classificacao = state["classificacoes"].get(nome, "non-AI")

        # 1. Monta a query para buscar informações relevantes no Qdrant
        query = (
            f"{startup['descricao_curta']} "
            f"Setor: {startup['setor']}. "
            f"Classificação de maturidade em IA: {classificacao}."
        )

        # 2. Recupera candidatos amplos e refina a seleção com Cohere.
        #    Isso evita descartar antes do rerank um case relevante, como o da Writer.
        documentos_relevantes = buscar_documentos_relevantes(
            query,
            k_inicial=30,
            top_n_final=4,
        )
        evidencias[nome] = [
            {
                "produto": doc.metadata.get("produto", "NVIDIA"),
                "url": doc.metadata.get("url_fonte", ""),
            }
            for doc in documentos_relevantes
        ]

        # 3. Junta os trechos que efetivamente serão enviados ao LLM
        trechos_nvidia = "\n\n---\n\n".join(
            "[Produto: {produto} | Fonte: {fonte}]\n{texto}".format(
                produto=doc.metadata.get("produto", "NVIDIA"),
                fonte=doc.metadata.get("url_fonte", "fonte não informada"),
                texto=doc.page_content,
            )
            for doc in documentos_relevantes
        )

        # 4. Preenche o prompt
        prompt = PROMPT_TEMPLATE.format(
            nome=nome,
            setor=startup["setor"],
            descricao_curta=startup["descricao_curta"],
            classificacao=classificacao,
            trechos_nvidia=trechos_nvidia
        )
        alertas_anteriores = state.get("alertas_validacao", {}).get(nome, [])
        if alertas_anteriores:
            prompt += (
                "\n\nREVISÃO APÓS VALIDAÇÃO: a tentativa anterior mencionou tecnologia(s) "
                f"não reconhecida(s): {', '.join(alertas_anteriores)}. "
                "Não repita esses nomes; use apenas produtos NVIDIA evidenciados nos trechos."
            )

        # 5. Chama o LLM
        resposta = llm.invoke(prompt)

        # 6. Guarda a recomendação
        recomendacoes[nome] = resposta.content.strip()

    return {"recomendacoes": recomendacoes, "evidencias": evidencias}


if __name__ == "__main__":
    from retriever_agent import retriever_agent
    from classifier_agent import classifier_agent

    state = {"consulta": "teste", "startups_encontradas": [], "classificacoes": {}, "recomendacoes": {}}
    state.update(retriever_agent(state))

    state["startups_encontradas"] = [
        s for s in state["startups_encontradas"] if s["nome"] == "Maritaca AI"
    ]

    state.update(classifier_agent(state))
    resultado = recommender_agent(state)

    for nome, recomendacao in resultado["recomendacoes"].items():
        print(f"\n=== {nome} ===")
        print(recomendacao)
