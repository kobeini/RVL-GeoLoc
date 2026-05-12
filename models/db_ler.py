import psycopg2
from config import db_parametros

def executar_sql(caminho):
    conn = psycopg2.connect(
    database=f"{db_parametros["bd"]}",
    user=f"{db_parametros["usuario"]}",
    password=f"{db_parametros["senha"]}",
    host=f"{db_parametros["host"]}",
    port=f"{db_parametros["porta"]}"
)