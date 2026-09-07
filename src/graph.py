from langgraph.graph import StateGraph, START, END
from state import RadarState

# Importando todos os agentes, incluindo o novo
from agents.query_planner_agent import query_planner_agent
from agents.retriever_agent import retriever_agent
from agents.classifier_agent import classifier_agent
from agents.recommender_agent import recommender_agent
from agents.evidence_validator_agent import evidence_validator_agent
from agents.briefing_agent import briefing_agent



def build_graph():
    grafo = StateGraph(RadarState)

    # 1. Adicionando todos os nós
    grafo.add_node("query_planner", query_planner_agent) # Novo nó
    grafo.add_node("retriever", retriever_agent)
    grafo.add_node("classifier", classifier_agent)
    grafo.add_node("recommender", recommender_agent)
    grafo.add_node("evidence_validator", evidence_validator_agent)
    grafo.add_node("briefing", briefing_agent)

    # 2. Definindo o novo fluxo (Arestas)
    grafo.add_edge(START, "query_planner")             # O fluxo agora começa aqui
    grafo.add_edge("query_planner", "retriever")       # O planner passa os critérios para o retriever
    grafo.add_edge("retriever", "classifier")
    grafo.add_edge("classifier", "recommender")
    grafo.add_edge("recommender", "evidence_validator")
    grafo.add_conditional_edges(
        "evidence_validator",
        _proximo_passo_apos_validacao,
        {"retry": "recommender", "briefing": "briefing"},
    )
    grafo.add_edge("briefing", END)
    return grafo.compile()


def _proximo_passo_apos_validacao(state):
    """Permite uma única recomposição quando o validador encontra erro."""
    if state.get("alertas_validacao") and state.get("tentativas_validacao", 0) < 2:
        return "retry"
    return "briefing"


if __name__ == "__main__":
    app = build_graph()

    state_inicial = {
        "consulta": "startups de saúde usando IA",
        "criterios_busca": {}, # <-- É bom inicializar vazio no estado inicial
        "startups_encontradas": [],
        "classificacoes": {},
        "fontes_startup": {},
        "recomendacoes": {},
        "alertas_validacao": {},
        "evidencias": {},
        "briefing": "",
        "tentativas_validacao": 0,
    }

    resultado_final = app.invoke(state_inicial)

    print("\n=== CLASSIFICAÇÕES ===")
    for nome, classe in resultado_final["classificacoes"].items():
        print(f"{nome}: {classe}")

    print("\n=== RECOMENDAÇÕES ===")
    for nome, rec in resultado_final["recomendacoes"].items():
        print(f"\n--- {nome} ---")
        print(rec[:300], "...")
