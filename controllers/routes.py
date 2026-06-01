# routes.py
from flask import Flask, render_template, redirect, url_for, request, flash, session
from config import db
from controllers.db_conversor import Conversor
from models.database.db_usuario import Usuario
from markupsafe import Markup
from werkzeug.security import generate_password_hash, check_password_hash

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
            usuario = Usuario.query.filter_by(email=email).first()
            if usuario:
                msgUsuario = Markup("Usuário já cadastrado. Faça o login")
                flash(msgUsuario, 'danger')
                return redirect(url_for('cadastro'))
            senha_hash = generate_password_hash(senha, method='scrypt')
            novousuario = Usuario(email=email,senha=senha_hash, nome=nome, permissao=None)
            db.session.add(novousuario)
            db.session.commit()
            msgCad = Markup("Cadastro realizado com sucesso!")
            flash(msgCad, 'sucesss')
            return redirect(url_for('cadastro'))
        return render_template('cadastro.html', pagina = 'cadastro')
    
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == "POST":
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha'] 
            
            usuario = Usuario.query.filter_by(email=email).first()
            if usuario:
                if check_password_hash(usuario.senha, senha):
                    session['usuario_id'] = usuario.id
                    session['usuario_email'] = usuario.email
                    msgLogin = "Login realizado"
                    flash(msgLogin, 'sucess')
                    redirect(url_for('index'))
                else:
                    msgLogin = "Login não autorizado"
                    flash(msgLogin, 'danger')
        return render_template('login.html', pagina = 'login')
    
    
    @app.route('/mapa')
    def mapa():
        gdf_uniao, gdf_lito, gdf_estados = Conversor.postgis_to_gdf()
        map_html = Conversor.gdf_to_html(
        gdf_uniao, gdf_lito, gdf_estados,
        camada_nome="Áreas Classificadas",
        geojson_path="static/database/minas.geojson"
    )
        return render_template('mapa.html', mapa_html= map_html, pagina = 'mapa')
    
