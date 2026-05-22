from flask import Flask
from controllers import routes
from models.database import db_usuario
from config import db_url, db_nome, db
import os
import pymysql


app = Flask(__name__, template_folder='views')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://root@localhost/{db_nome['projeto']}'
routes.init_app(app)

if __name__ == '__main__':
    connection = pymysql.connect(host='localhost',user='root',password='',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            cursor.execute(f'CREATE DATABASE IF NOT EXISTS {db_nome['projeto']}')
            print("o banco de dados está criado!")
    except Exception as error:
        print(f"Ocorreu um erro ao criar o banco de dados!' {error}")
    finally:
        connection.close()
    db.init_app(app=app)
    with app.test_request_context():
        db.create_all()
    app.run(debug=True)