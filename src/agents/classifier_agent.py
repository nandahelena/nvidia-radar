import time

from llm_factory import create_llm

llm = create_llm()

PROMPT_TEMPLATE = """
Você é um analista técnico especializado em avaliar o papel da Inteligência Artificial no produto de uma startup.

Sua tarefa é classificar a startup em exatamente uma das três categorias abaixo:

- AI-native: a Inteligência Artificial é essencial para o funcionamento e para a proposta de valor principal do produto. O produto depende de modelos de IA para existir ou entregar sua principal funcionalidade. Remover a IA descaracterizaria o produto.

- AI-enabled: a empresa possui um produto ou serviço que poderia existir sem Inteligência Artificial, mas utiliza IA para adicionar, melhorar ou automatizar funcionalidades específicas. A IA é importante, mas não é o núcleo indispensável do produto.

- non-AI: a Inteligência Artificial não possui papel relevante na proposta de valor ou no funcionamento principal do produto. Eventuais usos internos ou secundários de IA não são suficientes para classificar a empresa como AI-enabled.

CRITÉRIO PRINCIPAL:
Avalie o papel da IA no CORE do produto, e não apenas se a empresa utiliza alguma tecnologia de IA.

Considere principalmente:
1. Qual é a principal proposta de valor do produto?
2. A IA é necessária para entregar essa proposta de valor?
3. O produto continuaria existindo e mantendo sua função principal sem IA?
4. A IA é o produto em si ou apenas uma funcionalidade dentro dele?

IMPORTANTE:
- Não classifique uma empresa como AI-native apenas porque ela utiliza IA em alguma parte do produto.
- Não classifique como AI-enabled apenas porque a empresa utiliza IA internamente.
- Baseie a classificação nas informações fornecidas sobre o produto e o negócio.
- Se houver informações conflitantes, priorize as evidências mais diretamente relacionadas ao produto principal.
- Não faça suposições que não estejam apoiadas pelas informações fornecidas.

Startup: {nome}
Setor: {setor}
Descrição: {descricao_curta}

Documentos sobre a empresa:
{textos_dos_documentos}

Responda APENAS com uma das três opções exatas:
AI-native
AI-enabled
non-AI
"""

MAX_CARACTERES_POR_DOCUMENTO = 800

def classifier_agent(state):
    classificacoes = {}
    fontes_startup = {}

    for startup in state["startups_encontradas"]:

        textos_dos_documentos = "\n\n".join(
            doc["conteudo_texto"][:MAX_CARACTERES_POR_DOCUMENTO]
            for doc in startup["documentos"]
        )
        fontes_startup[startup["nome"]] = [
            {
                "titulo": doc.get("titulo", "Documento da startup"),
                "url": doc.get("url_fonte", ""),
            }
            for doc in startup.get("documentos", [])
            if doc.get("url_fonte")
        ]

        prompt_preenchido = PROMPT_TEMPLATE.format(
            nome=startup["nome"],
            setor=startup["setor"],
            descricao_curta=startup["descricao_curta"],
            textos_dos_documentos=textos_dos_documentos
        )

        resposta = llm.invoke(prompt_preenchido)
        time.sleep(15)

        classificacoes[startup["nome"]] = resposta.content.strip()

    return {"classificacoes": classificacoes, "fontes_startup": fontes_startup}

if __name__ == "__main__":
    from retriever_agent import retriever_agent
    
    state_inicial = {"consulta": "teste", "startups_encontradas": [], "classificacoes": {}, "recomendacoes": {}}
    state_com_startups = retriever_agent(state_inicial)
    
    resultado = classifier_agent(state_com_startups)
    
    for nome, classificacao in resultado["classificacoes"].items():
        print(f"{nome}: {classificacao}")
