"""Monta o briefing executivo final sem uma chamada adicional ao LLM."""


def score_risco_commoditizacao(startup, classificacao):
    """Heurística transparente para destacar dependência de capacidades genéricas."""
    texto = f"{startup.get('descricao_curta', '')} {classificacao}".lower()
    sinais = ("llm", "modelo", "inteligência artificial", "ia", "chatbot", "automação")
    pontos = sum(sinal in texto for sinal in sinais)
    if classificacao == "AI-native" or pontos >= 3:
        return "alto"
    if classificacao == "AI-enabled" or pontos >= 1:
        return "médio"
    return "baixo"


def briefing_agent(state):
    linhas = ["# Briefing executivo — NVIDIA Startup AI Radar", ""]
    linhas.append(f"Startups analisadas: {len(state.get('startups_encontradas', []))}")
    linhas.append("")

    for startup in state.get("startups_encontradas", []):
        nome = startup["nome"]
        classificacao = state.get("classificacoes", {}).get(nome, "não classificada")
        risco = score_risco_commoditizacao(startup, classificacao)
        recomendacao = state.get("recomendacoes", {}).get(nome, "Nenhuma recomendação encontrada.")
        fontes_startup = state.get("fontes_startup", {}).get(nome, [])
        linhas.extend([
            f"## {nome}",
            f"Classificação: {classificacao}",
            f"Risco de comoditização: {risco}",
            "",
            recomendacao,
            "",
        ])
        if fontes_startup:
            linhas.append("Fontes da startup usadas na classificação:")
            linhas.extend(f"- {fonte['titulo']}: {fonte['url']}" for fonte in fontes_startup)
            linhas.append("")

    alertas = state.get("alertas_validacao", {})
    if alertas:
        linhas.extend(["## Alertas de validação", ""])
        for nome, itens in alertas.items():
            linhas.append(f"- {nome}: {', '.join(itens)}")

    return {"briefing": "\n".join(linhas)}
