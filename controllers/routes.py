# routes.py (modificado)
from flask import Flask, render_template_string, redirect, url_for
from controllers.db_conversor import Conversor

app = Flask(__name__)

def init_app(app):
    @app.route('/')
    def index():
        return redirect(url_for('mapa'))

    @app.route('/mapa')
    def mapa():
        mapa = Conversor.postgis_to_gdf()
        mapa_html = Conversor.gdf_to_html(mapa, camada_nome="Análise")
        return render_template_string(mapa_html)