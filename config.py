from sqlalchemy import create_engine


db_parametros = {
    "usuario" : 'postgres',
    "senha" : 'nainha04131120@',
    "host":'localhost',
    "porta": '5432',
    "bd" : 'rvlgeoloc'
}
db_url = f'postgresql://{db_parametros["usuario"]}:{db_parametros["senha"]}{db_parametros["host"]}:{db_parametros["porta"]}/{db_parametros["bd"]}'
engine = create_engine(db_url)
query_lito = "select * from public.banco_lito where lower(litotipo2) like '%%carbonatito%%' or lower(litotipo1) like '%% piroxenito%%'"
query_estados = "select * from public.teste where nome like '%%São Paulo%%'"
url_database = "./static/database/"
