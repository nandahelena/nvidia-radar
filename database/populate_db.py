import json
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.getenv("DATABASE_URL")

def insert_startup(cursor, dados_startup):
    cursor.execute(
        """
        INSERT INTO startups (
            nome,
            site,
            setor,
            estagio,
            localizacao,
            descricao_curta,
            ano_fundacao,
            tamanho_time
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            dados_startup["nome"],
            dados_startup["site"],
            dados_startup["setor"],
            dados_startup["estagio"],
            dados_startup["localizacao"],
            dados_startup["descricao_curta"],
            dados_startup["ano_fundacao"],
            dados_startup["tamanho_time"],
        )
    )

    return cursor.fetchone()[0]


def insert_documento(cursor, startup_id, dados_documento):
    cursor.execute(
        """
        INSERT INTO documentos (
            startup_id,
            tipo,
            titulo,
            conteudo_texto,
            url_fonte,
            data_publicacao
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            startup_id,
            dados_documento["tipo"],
            dados_documento["titulo"],
            dados_documento["conteudo_texto"],
            dados_documento["url_fonte"],
            dados_documento["data_publicacao"],
        )
    )


def main():
    with psycopg2.connect(db_url) as connection:
        with connection.cursor() as cursor:
            
            cursor.execute("TRUNCATE TABLE documentos, startups RESTART IDENTITY CASCADE;")
            
            arquivos = Path("data/startups").glob("*.json")
            for arquivo in arquivos:
                with open(arquivo, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                
                print(f"Inserindo {dados['nome']}... ", end="")
                startup_id = insert_startup(cursor, dados)
                for documento in dados["documentos"]:
                    insert_documento(cursor, startup_id, documento)
                print(f"OK (id={startup_id}, {len(dados['documentos'])} docs)")


if __name__ == "__main__":
    main()