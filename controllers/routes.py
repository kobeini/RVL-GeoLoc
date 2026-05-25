# routes.py
from flask import Flask, render_template, redirect, url_for, request
from config import db
from controllers.db_conversor import Conversor
from models.database.db_usuario import Usuario
from werkzeug.security import generate_password_hash

app = Flask(__name__, template_folder='views')

def init_app(app):
    @app.route('/')
    def index():
        return render_template('index.html', pagina = 'index')
    
    
    @app.route('/conta', methods=['GET', 'POST'])
    def perfil():
        lerUsuario = Usuario.query.all()
        return render_template('perfil.html', lerUsuario = lerUsuario, pagina = 'perfil')
    

    @app.route('/cadastro', methods=['GET', 'POST'])
    def cadastro():
        if request.method == "POST":
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha']
            senha_hash = generate_password_hash(senha, method='scrypt')
            novousuario = Usuario(email=email,senha=senha_hash, nome=nome, permissao=None)
            db.session.add(novousuario)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('cadastro.html', pagina = 'cadastro')
    
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == "POST":
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha'] 
            return redirect(url_for('cadastro'))
        return render_template('cadastro.html', pagina = 'login')
    
    
    @app.route('/mapa')
    def mapa():
        gdf_uniao, gdf_lito, gdf_estados = Conversor.postgis_to_gdf()
        map_html = Conversor.gdf_to_html(
        gdf_uniao, gdf_lito, gdf_estados,
        camada_nome="Áreas Classificadas",
        geojson_path="static/database/minas.geojson"
    )
        return render_template('mapa.html', mapa_html= map_html, pagina = 'mapa')
    
