import json
import html as html_lib
import os
import re
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from graph import build_graph

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------

st.set_page_config(
    page_title="NVIDIA Startup AI Radar",
    page_icon=os.path.join(os.path.dirname(__file__), "assets", "nvidia-radar-logo.svg"),
    layout="wide",
    initial_sidebar_state="expanded",
)

EXEMPLOS_CONSULTA = [
    "startups de saúde usando IA",
    "startups AI-native",
    "startups de logística e industria",
]

CLASSIFICACAO_INFO = {
    "AI-native": {"icone": "radio_button_checked", "cor": "#76B900", "cor_fundo": "rgba(118, 185, 0, 0.14)"},
    "AI-enabled": {"icone": "radio_button_checked", "cor": "#E8B339", "cor_fundo": "rgba(232, 179, 57, 0.14)"},
    "non-AI": {"icone": "radio_button_checked", "cor": "#9AA0A6", "cor_fundo": "rgba(154, 160, 166, 0.14)"},
}

PRIORIDADE_COR = {"alta": "#E5484D", "média": "#E8B339", "media": "#E8B339", "baixa": "#7C8591"}
COMPLEXIDADE_COR = {"alta": "#E5484D", "média": "#E8B339", "media": "#E8B339", "baixa": "#76B900"}


# --------------------------------------------------------------------------
# Estilo
# --------------------------------------------------------------------------

st.markdown(
    """
    <style>
        :root { --nv-green: #76B900; --nv-ink: #F2F5F7; --nv-muted: #9AA0A6; --nv-line: rgba(255,255,255,0.10); }
        .stApp { background: radial-gradient(circle at 75% 0%, rgba(118,185,0,0.08), transparent 34rem), #0E1012; }
        .block-container { padding-top: 2.4rem; padding-bottom: 4rem; max-width: 1180px; }
        section[data-testid="stSidebar"] { background: #121518; border-right: 1px solid var(--nv-line); }
        section[data-testid="stSidebar"] .block-container { padding: 1.6rem 1.25rem; }

        .radar-hero {
            display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.35rem;
        }
        .radar-hero h1 { margin: 0; font-size: 2.35rem; letter-spacing: -0.04em; }
        .radar-kicker { color: var(--nv-green); font-size: 0.72rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 0.3rem; }
        .radar-subtitle { color: var(--nv-muted); font-size: 1.02rem; line-height: 1.55; max-width: 760px; margin-bottom: 0.65rem; }
        .search-lead { display: flex; align-items: center; gap: 0.55rem; color: var(--nv-ink); font-size: 1rem; font-weight: 700; margin: 0.45rem 0 0.55rem; }
        .search-lead-icon { position: relative; display: inline-block; width: 1rem; height: 1rem; border: 2px solid var(--nv-green); border-radius: 50%; box-sizing: border-box; }
        .search-lead-icon::after { content: ''; position: absolute; width: 0.45rem; height: 2px; right: -0.34rem; bottom: -0.14rem; background: var(--nv-green); transform: rotate(45deg); transform-origin: left center; border-radius: 2px; }
        .search-hint { color: var(--nv-muted); font-size: 0.82rem; margin-bottom: 0.55rem; }
        div[data-testid="stTextInput"] { margin-bottom: 0.55rem; }
        div[data-testid="stTextInput"] label { display: none; }
        div[data-testid="stTextInput"] input { height: 2.8rem; min-height: 2.8rem; border: 1px solid rgba(118,185,0,0.52); border-radius: 10px; background: rgba(255,255,255,0.055); padding: 0 1rem; font-size: 1rem; box-shadow: 0 0 0 3px rgba(118,185,0,0.06); }
        div[data-testid="stTextInput"] input:focus { border-color: var(--nv-green); box-shadow: 0 0 0 3px rgba(118,185,0,0.14); }
        div[data-testid="stButton"]:has(button[kind="primary"]) { margin-top: 0; }
        div[data-testid="stButton"] button[kind="primary"] { height: 2.8rem; min-height: 2.8rem; border-radius: 10px; font-weight: 700; box-shadow: 0 8px 22px rgba(118,185,0,0.18); }
        .section-label { color: var(--nv-muted); font-size: 0.78rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
        .flow-step { display: flex; gap: 0.7rem; align-items: flex-start; padding: 0.65rem 0; border-bottom: 1px solid rgba(255,255,255,0.07); }
        .flow-step:last-child { border-bottom: 0; }
        .flow-icon { color: var(--nv-green); font-size: 1.15rem; line-height: 1.2; }
        .flow-copy { color: #C9CDD3; font-size: 0.82rem; line-height: 1.4; }
        .flow-copy b { color: var(--nv-ink); }
        .startup-row { display: flex; justify-content: space-between; gap: 0.6rem; font-size: 0.79rem; padding: 0.38rem 0; color: #C9CDD3; border-bottom: 1px solid rgba(255,255,255,0.06); }
        .startup-row b { color: var(--nv-ink); }
        .startup-sector { color: var(--nv-muted); text-align: right; }
        .legend-row { display: flex; align-items: center; gap: 0.45rem; padding: 0.25rem 0; color: #C9CDD3; font-size: 0.84rem; }
        .legend-dot { font-size: 0.9rem; }

        .pill {
            display: inline-block; padding: 0.18rem 0.65rem; border-radius: 999px;
            font-size: 0.78rem; font-weight: 600; margin-right: 0.4rem; margin-bottom: 0.3rem;
            border: 1px solid var(--nv-line);
        }

        .tech-card {
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 10px;
            padding: 0.9rem 1.1rem;
            margin-bottom: 0.9rem;
            background: rgba(255,255,255,0.035);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }
        .tech-card h4 { margin: 0 0 0.5rem 0; color: var(--nv-green); }
        .tech-card p { margin: 0.25rem 0; font-size: 0.92rem; line-height: 1.45; }
        .tech-card .label { color: #9AA0A6; font-weight: 600; }

        div[data-testid="stExpander"] {
            border: 1px solid var(--nv-line) !important;
            border-radius: 12px !important;
            margin-bottom: 0.6rem;
            background: rgba(255,255,255,0.018);
        }
        div[data-testid="stMetric"] { border-left: 2px solid var(--nv-green); padding-left: 0.8rem; }
        div[data-testid="stButton"] button { border-radius: 8px; border-color: var(--nv-line); transition: border-color 160ms ease, background 160ms ease; }
        div[data-testid="stButton"] button:hover { border-color: rgba(118,185,0,0.65); background: rgba(118,185,0,0.08); }
        div[data-testid="stTextInput"] input { border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------

def carregar_startups_config():
    caminho = os.path.join(os.path.dirname(__file__), "data", "startups_config.json")
    try:
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


with st.sidebar:
    st.markdown("### :material/radar: NVIDIA Startup AI Radar")
    st.caption("Radar de maturidade em IA e recomendação de tecnologias NVIDIA para startups brasileiras.")

    st.markdown("---")
    st.markdown("<div class='section-label'>Como funciona</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='flow-step'><span class='flow-icon'>▦</span><span class='flow-copy'><b>Retriever</b><br/>Busca startups e documentos na base</span></div>"
        "<div class='flow-step'><span class='flow-icon'>◈</span><span class='flow-copy'><b>Classifier</b><br/>Avalia a maturidade do produto em IA</span></div>"
        "<div class='flow-step'><span class='flow-icon'>↗</span><span class='flow-copy'><b>Recommender</b><br/>Cruza o perfil com a documentação NVIDIA</span></div>",
        unsafe_allow_html=True,
    )

    startups_config = carregar_startups_config()
    if startups_config:
        st.markdown("---")
        st.markdown(f"<div class='section-label'>Base de startups <span style='color:#76B900'>· {len(startups_config)}</span></div>", unsafe_allow_html=True)
        for s in startups_config:
            st.markdown(
                f"<div class='startup-row'><b>{s['nome']}</b><span class='startup-sector'>{s.get('setor', '')}</span></div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("<div class='section-label'>Legenda de classificação</div>", unsafe_allow_html=True)
    for label, info in CLASSIFICACAO_INFO.items():
        st.markdown(
            f"<div class='legend-row'><span class='legend-dot' style='color:{info['cor']}'>●</span>{label}</div>",
            unsafe_allow_html=True,
        )


# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------

st.markdown(
    "<div class='radar-kicker'>NVIDIA Developer Intelligence</div>"
    "<div class='radar-hero'><h1>NVIDIA Startup AI Radar</h1></div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='radar-subtitle'>Analise startups brasileiras e receba recomendações de tecnologias NVIDIA "
    "com base na maturidade em IA de cada produto.</div>",
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------
# Exemplos de consulta
# --------------------------------------------------------------------------

def _definir_consulta(texto):
    st.session_state["consulta_input"] = texto


st.markdown(
    "<div class='search-lead'><span class='search-lead-icon'></span> Encontre startups por contexto</div>",
    unsafe_allow_html=True,
)
st.caption("Sugestões rápidas")
cols = st.columns(len(EXEMPLOS_CONSULTA))
for col, exemplo in zip(cols, EXEMPLOS_CONSULTA):
    col.button(exemplo, on_click=_definir_consulta, args=(exemplo,), use_container_width=True)

campo_consulta, acao_busca = st.columns([5, 1], gap="small")
with campo_consulta:
    consulta = st.text_input(
        "O que você está buscando?",
        key="consulta_input",
        placeholder="ex: startups de saúde usando IA",
    )
with acao_busca:
    buscar = st.button(":material/search:  Analisar", type="primary", use_container_width=True)


# --------------------------------------------------------------------------
# Helpers de renderização
# --------------------------------------------------------------------------

def badge(texto, cor, cor_fundo=None):
    fundo = cor_fundo or f"{cor}22"
    return f"<span class='pill' style='color:{cor}; background:{fundo};'>{texto}</span>"


def normalizar_classificacao(classificacao):
    texto = (classificacao or "").strip()
    for chave in CLASSIFICACAO_INFO:
        if chave.lower() in texto.lower():
            return chave
    return "non-AI"


def parse_recomendacao(texto):
    """Extrai blocos estruturados 'Tecnologia: ...' da resposta do recommender."""
    texto_sem_links = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", texto or "")
    cabecalhos = list(re.finditer(r"(?m)^\s*#{2,6}\s*(.+?)\s*$", texto_sem_links))
    if cabecalhos and not re.search(r"Tecnologia\s*:", texto_sem_links, re.IGNORECASE):
        blocos_markdown = []
        for cabecalho, proximo_cabecalho in zip(cabecalhos, cabecalhos[1:] + [None]):
            fim = proximo_cabecalho.start() if proximo_cabecalho else len(texto_sem_links)
            nome = limpar_markdown(cabecalho.group(1))
            corpo = limpar_markdown(texto_sem_links[cabecalho.end():fim])
            blocos_markdown.append(f"Tecnologia: {nome} {corpo}")
        texto = " ".join(blocos_markdown)
    else:
        texto = limpar_markdown(texto)
    if not texto:
        return []

    rotulos = (
        "Tecnologia", "Prioridade", "Complexidade de implementação",
        "Justificativa técnica", "Justificativa de negócio", "Próxima ação sugerida",
        "Evidências usadas",
    )
    rotulo_regex = "|".join(re.escape(rotulo) for rotulo in rotulos)
    campos = {
        "tecnologia": "Tecnologia",
        "prioridade": "Prioridade",
        "complexidade": "Complexidade de implementação",
        "justificativa_tecnica": "Justificativa técnica",
        "justificativa_negocio": "Justificativa de negócio",
        "proxima_acao": "Próxima ação sugerida",
        "evidencias": "Evidências usadas",
    }

    recomendacoes = []
    ocorrencias = list(re.finditer(rf"(?P<rotulo>{rotulo_regex})\s*:", texto, re.IGNORECASE))
    inicios_tecnologia = [ocorrencia for ocorrencia in ocorrencias if ocorrencia.group("rotulo").lower() == "tecnologia"]
    for inicio, proximo_tecnologia in zip(inicios_tecnologia, inicios_tecnologia[1:] + [None]):
        fim_bloco = proximo_tecnologia.start() if proximo_tecnologia else len(texto)
        bloco = texto[inicio.end():fim_bloco].strip()
        dados = {campo: "" for campo in campos}
        for ocorrencia, proxima_ocorrencia in zip(ocorrencias, ocorrencias[1:] + [None]):
            if ocorrencia.start() < inicio.start() or ocorrencia.start() >= fim_bloco:
                continue
            campo = next((nome for nome, rotulo in campos.items() if rotulo.lower() == ocorrencia.group("rotulo").lower()), None)
            if not campo:
                continue
            fim_campo = proxima_ocorrencia.start() if proxima_ocorrencia and proxima_ocorrencia.start() < fim_bloco else fim_bloco
            dados[campo] = texto[ocorrencia.end():fim_campo].strip()
        if dados.get("tecnologia"):
            recomendacoes.append(dados)
    return recomendacoes


def limpar_markdown(texto):
    """Remove formatação Markdown que o recommender pode misturar ao texto estruturado."""
    if not texto:
        return ""
    texto = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", texto)
    texto = re.sub(r"^\s*#{1,6}\s*", "", texto, flags=re.MULTILINE)
    texto = texto.replace("---", " ")
    texto = re.sub(r"[*_`]+", "", texto)
    texto = re.sub(r"[ \t]+", " ", texto)
    return re.sub(r"\n{3,}", "\n\n", texto).strip()


def render_recomendacao(texto):
    itens = parse_recomendacao(texto)
    if not itens:
        st.markdown(limpar_markdown(texto))
        return

    for item in itens:
        prioridade = item.get("prioridade", "").lower()
        complexidade = item.get("complexidade", "").lower()
        p_cor = PRIORIDADE_COR.get(prioridade, "#7C8591")
        c_cor = COMPLEXIDADE_COR.get(complexidade, "#7C8591")

        chips = ""
        if item.get("prioridade"):
            chips += badge(f"Prioridade: {item['prioridade']}", p_cor)
        if item.get("complexidade"):
            chips += badge(f"Complexidade: {item['complexidade']}", c_cor)

        tecnologia = html_lib.escape(item["tecnologia"])
        rendered_html = f"<div class='tech-card'><h4><span style='color:#9AA0A6'>◈</span> {tecnologia}</h4>"
        rendered_html += chips + "<br/><br/>"
        if item.get("justificativa_tecnica"):
            rendered_html += f"<p><span class='label'>Justificativa técnica:</span> {html_lib.escape(item['justificativa_tecnica'])}</p>"
        if item.get("justificativa_negocio"):
            rendered_html += f"<p><span class='label'>Justificativa de negócio:</span> {html_lib.escape(item['justificativa_negocio'])}</p>"
        if item.get("proxima_acao"):
            rendered_html += f"<p><span class='label'>Próxima ação sugerida:</span> {html_lib.escape(item['proxima_acao'])}</p>"
        if item.get("evidencias"):
            evidencias = item["evidencias"]
            links = re.findall(r"https?://[^\s)]+", evidencias)
            if links:
                evidencias_html = " ".join(
                    f'<a href="{html_lib.escape(link, quote=True)}" target="_blank">{html_lib.escape(link)}</a>'
                    for link in links
                )
            else:
                evidencias_html = html_lib.escape(evidencias)
            rendered_html += f"<p><span class='label'>Evidências usadas:</span> {evidencias_html}</p>"
        rendered_html += "</div>"

        st.markdown(rendered_html, unsafe_allow_html=True)


def briefing_markdown(resultado):
    """Gera o arquivo exportável a partir do estado final do grafo."""
    return resultado.get("briefing", "# Briefing executivo\n\nNenhum resultado.")


# --------------------------------------------------------------------------
# Execução da busca
# --------------------------------------------------------------------------

if buscar:
    if not consulta:
        st.warning("Digite uma consulta antes de buscar.")
    else:
        resultado = None
        with st.spinner("Analisando startups e gerando recomendações..."):
            try:
                app = build_graph()
                state_inicial = {
                    "consulta": consulta,
                    "criterios_busca": {},
                    "startups_encontradas": [],
                    "classificacoes": {},
                    "fontes_startup": {},
                    "recomendacoes": {},
                    "alertas_validacao": {},
                    "evidencias": {},
                    "briefing": "",
                    "tentativas_validacao": 0,
                }
                resultado = app.invoke(state_inicial)
            except Exception as e:
                mensagem = str(e)
                if "429" in mensagem or "rate_limit" in mensagem.lower() or "tokens per day" in mensagem.lower():
                    st.warning(
                        "O provedor de linguagem atingiu o limite diário de tokens. "
                        "A interface está funcionando, mas será necessário aguardar a "
                        "renovação da quota ou usar outra chave/modelo."
                    )
                else:
                    st.error(f"Ocorreu um erro ao processar a consulta: {e}")

        if resultado:
            startups = resultado["startups_encontradas"]

            if not startups:
                st.info(
                    "Nenhuma startup encontrada para esses critérios. "
                    "Tente uma consulta mais ampla, como 'startups AI-native' "
                    "ou 'startups de saúde usando IA'."
                )
                st.stop()

            contagem = {"AI-native": 0, "AI-enabled": 0, "non-AI": 0}
            for s in startups:
                classe = normalizar_classificacao(resultado["classificacoes"].get(s["nome"]))
                contagem[classe] += 1

            st.markdown("#### Visão geral")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Startups analisadas", len(startups))
            m2.metric("AI-native", contagem["AI-native"])
            m3.metric("AI-enabled", contagem["AI-enabled"])
            m4.metric("non-AI", contagem["non-AI"])

            st.markdown("#### Resultados por startup")

            for startup in startups:
                nome = startup["nome"]
                setor = startup.get("setor", "")
                classificacao_raw = resultado["classificacoes"].get(nome, "non-AI")
                classe = normalizar_classificacao(classificacao_raw)
                info = CLASSIFICACAO_INFO[classe]
                recomendacao = resultado["recomendacoes"].get(
                    nome, "Nenhuma recomendação encontrada."
                )

                with st.expander(f":material/radar:  {nome}  ·  {setor}"):
                    st.markdown(
                        badge(classe, info["cor"], info["cor_fundo"]),
                        unsafe_allow_html=True,
                    )
                    if startup.get("descricao_curta"):
                        st.caption(startup["descricao_curta"])

                    st.markdown("**Recomendações NVIDIA**")
                    render_recomendacao(recomendacao)

                    alertas = resultado.get("alertas_validacao", {}).get(nome, [])
                    if alertas:
                        st.warning(
                            "Recomendação bloqueada pelo validador: "
                            + ", ".join(alertas)
                        )

            st.download_button(
                label=":material/download: Exportar briefing (.md)",
                data=briefing_markdown(resultado),
                file_name="nvidia_startup_ai_radar_briefing.md",
                mime="text/markdown",
                use_container_width=True,
            )
