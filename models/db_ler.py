import os
import psycopg2
from config import db_parametros

def executar_sql(caminho):
    conn = psycopg2.connect(
        database=db_parametros["bd"],
        user=db_parametros["usuario"],
        password=db_parametros["senha"],
        host=db_parametros["host"],
        port=db_parametros["porta"]
    )
    try:
        with conn.cursor() as cur:
            with open(caminho, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            cur.execute(sql_script)
        conn.commit()
        print("Banco de Dados setado.")
    except Exception as e:
        print(f"Erro: {e}")
        conn.rollback()
    finally:
        conn.close()