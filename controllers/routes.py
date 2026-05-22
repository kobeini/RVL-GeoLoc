# routes.py
from flask import Flask, render_template, redirect, url_for, request
from config import db
from controllers.db_conversor import Conversor
from models.database.db_usuario import Usuario

app = Flask(__name__, template_folder='views')

def init_app(app):
    @app.route('/')
    def index():
        return render_template('index.html', pagina = 'index')
    
    
    @app.route('/conta', methods=['GET', 'POST'])
    def perfil():
        if request.method == 'POST':
            dados = request.form.to.dict()
            newuser = Usuario(dados['nome'], dados['email'])
            db.session.add(newuser)
            db.session.commit()
            return redirect(url_for('perfil'))
        lerUsuario = Usuario.query.all()
        return render_template('perfil.html', lerUsuario = lerUsuario, pagina = 'perfil')
    

    @app.route('/cadastro', methods=['GET', 'POST'])
    def cadastro():
        return render_template('cadastro.html', pagina = 'cadastro')
    
    
    @app.route('/mapa')
    def mapa():
        gdf_uniao, gdf_lito, gdf_estados = Conversor.postgis_to_gdf()
        map_html = Conversor.gdf_to_html(
        gdf_uniao, gdf_lito, gdf_estados,
        camada_nome="Áreas Classificadas",
        geojson_path="static/database/minas.geojson"
    )
        return render_template('mapa.html', mapa_html= map_html, pagina = 'mapa')
    
