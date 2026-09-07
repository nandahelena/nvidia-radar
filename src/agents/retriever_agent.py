from typing import TypedDict
import psycopg2
from dotenv import load_dotenv
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

db_url = os.getenv("DATABASE_URL")

class RadarState(TypedDict):
    consulta: str
    startups_encontradas: list
    classificacoes: dict
    recomendacoes: dict

def retriever_agent(state):
    # Pega os critérios definidos pelo query_planner, usando um dict vazio como fallback
    criterios = state.get("criterios_busca", {})

    with psycopg2.connect(db_url) as connection:
        with connection.cursor() as cursor:

            condicoes = []
            valores = []

            # 1. Filtro por Setor
            if criterios.get("setor"):
                condicoes.append("setor ILIKE %s")
                valores.append(f"%{criterios['setor']}%")

            # 2. Filtro por Estágio
            if criterios.get("estagio"):
                condicoes.append("estagio ILIKE %s")
                valores.append(f"%{criterios['estagio']}%")

            # 3. Filtro por Palavras-Chave (Corrigido para OR internamente)
            if criterios.get("palavras_chave"):
                condicoes_palavras = []
                for palavra in criterios["palavras_chave"]:
                    condicoes_palavras.append("descricao_curta ILIKE %s")
                    valores.append(f"%{palavra}%")
                
                # Agrupa as palavras-chave com OR entre si, dentro de parênteses.
                # Exemplo: (descricao_curta ILIKE '%saúde%' OR descricao_curta ILIKE '%IA%')
                condicoes.append("(" + " OR ".join(condicoes_palavras) + ")")

            sql_base = "SELECT id, nome, setor, descricao_curta FROM startups"

            # Monta a query final unindo os grandes blocos com AND
            if condicoes:
                sql = sql_base + " WHERE " + " AND ".join(condicoes)
            else:
                sql = sql_base

            # Executa a busca das startups (protegido contra SQL Injection)
            cursor.execute(sql, valores)
            linhas = cursor.fetchall()

            startups = [
                {"id": l[0], "nome": l[1], "setor": l[2], "descricao_curta": l[3]}
                for l in linhas
            ]

            # 4. Buscando os documentos associados a cada startup encontrada
            for startup in startups:
                cursor.execute(
                    "SELECT tipo, titulo, conteudo_texto, url_fonte FROM documentos WHERE startup_id = %s",
                    (startup["id"],)
                )
                docs = cursor.fetchall()
                startup["documentos"] = [
                    {"tipo": d[0], "titulo": d[1], "conteudo_texto": d[2], "url_fonte": d[3]}
                    for d in docs
                ]

    # Retorna o dicionário para atualizar o estado do LangGraph
    return {"startups_encontradas": startups}

if __name__ == "__main__":
    resultado = retriever_agent({"consulta": "teste", "startups_encontradas": [], "classificacoes": {}, "recomendacoes": {}})
    print(f"{len(resultado['startups_encontradas'])} startups encontradas")
    print(resultado['startups_encontradas'][0])  # olha a primeira pra conferir estrutura