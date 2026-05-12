from flask import Flask
from controllers import routes
from config import db_url
from models.db_ler import executar_sql 
import os

app = Flask(__name__, template_folder='views')
routes.init_app(app)

if __name__ == '__main__':
    sql_path = os.path.join(os.path.dirname(__file__), 'static', 'database', 'banco_lito.sql')
    executar_sql(sql_path)
    
    app.run(debug=True)