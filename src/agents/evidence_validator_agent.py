import re


PRODUTOS_NVIDIA_VALIDOS = {
    "nim", "nemo", "nemo guardrails", "triton", "triton inference server",
    "tensorrt-llm", "tensorrt", "rapids", "cudf", "cuml", "cuda",
    "riva", "omniverse", "isaac", "clara", "morpheus",
    "ai enterprise", "nvidia ai enterprise", "cuopt", "inception"
}


_ROTULOS_SEGUINTES = (
    "Justificativa técnica", "Justificativa de negócio", "Prioridade",
    "Complexidade de implementação", "Próxima ação sugerida", "Evidências usadas",
    "Tecnologia",
)


def extrair_tecnologias(texto_recomendacao):
    """Extrai os nomes de tecnologia mencionados após 'Tecnologia:' no texto.

    O fallback textual (quando o structured output da Groq falha) nem sempre
    separa os campos com quebra de linha, então o corte precisa considerar
    também o próximo rótulo conhecido — não só '\\n' ou '*' — senão a
    justificativa inteira é capturada como se fosse o nome da tecnologia.
    """
    limite = "|".join(re.escape(rotulo) for rotulo in _ROTULOS_SEGUINTES)
    # Dois-pontos obrigatório: sem isso, "Tecnologia" batia dentro de
    # palavras como "tecnologias" no meio de frases soltas do fallback
    # textual, capturando a frase seguinte inteira como nome de produto.
    padrao = rf"Tecnologia\s*:\s*\**\s*(.+?)(?=\n|\*|(?:{limite})\s*:|\Z)"
    matches = re.findall(padrao, texto_recomendacao, re.IGNORECASE | re.DOTALL)
    return [m.strip() for m in matches]


def normalizar_nome(nome):
    """
    Remove o prefixo 'NVIDIA', deixa em minúsculas, remove espaços extras,
    para comparar de forma tolerante contra a whitelist.
    """
    # 1. Transforma o nome para minúsculas
    texto = nome.lower()

    # 2. Remove a palavra "nvidia"
    texto = texto.replace("nvidia", "").strip()

    # 3. Remove espaços duplicados
    texto = re.sub(r"\s+", " ", texto)

    return texto


def tecnologia_e_valida(nome):
    """Verifica se algum produto da whitelist aparece no texto capturado.

    Usa 'contém' em vez de igualdade exata porque o fallback textual da
    Groq (quando o structured output falha) nem sempre isola o nome do
    produto de frases ao redor — checar substring evita descartar uma
    recomendação legítima só por causa de uma captura com texto a mais,
    sem abrir mão de barrar produtos realmente inventados (ex.: "Arize").
    """
    nome_normalizado = normalizar_nome(nome)
    return any(produto in nome_normalizado for produto in PRODUTOS_NVIDIA_VALIDOS)


def evidence_validator_agent(state):
    recomendacoes = state["recomendacoes"]
    recomendacoes_validadas = {}
    alertas = {}

    for nome_startup, texto_recomendacao in recomendacoes.items():
        tecnologias_mencionadas = extrair_tecnologias(texto_recomendacao)

        tecnologias_invalidas = [
            t for t in tecnologias_mencionadas
            if not tecnologia_e_valida(t)
        ]

        if tecnologias_invalidas:
            alertas[nome_startup] = tecnologias_invalidas

            recomendacoes_validadas[nome_startup] = (
                f"[AVISO: recomendação original mencionava tecnologia(s) "
                f"não reconhecida(s) como produto NVIDIA: "
                f"{', '.join(tecnologias_invalidas)}. "
                f"Recomendação descartada por falha de validação de evidência.]"
            )
        else:
            recomendacoes_validadas[nome_startup] = texto_recomendacao

    return {
        "recomendacoes": recomendacoes_validadas,
        "alertas_validacao": alertas,
        "tentativas_validacao": state.get("tentativas_validacao", 0) + 1,
    }


if __name__ == "__main__":
    print(normalizar_nome("NVIDIA NIM"))
    print(normalizar_nome("Triton Inference Server"))
    print(tecnologia_e_valida("NVIDIA NIM"))
    print(tecnologia_e_valida("Sana"))
