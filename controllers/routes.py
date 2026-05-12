# routes.py
from flask import Flask, render_template, redirect, url_for
from controllers.db_conversor import Conversor

app = Flask(__name__, template_folder='views')

def init_app(app):
    @app.route('/')
    def index():
        return redirect(url_for('mapa'))

    @app.route('/mapa')
    def mapa():
        gdf_uniao, gdf_lito, gdf_estados = Conversor.postgis_to_gdf()
        map_html = Conversor.gdf_to_html(
        gdf_uniao, gdf_lito, gdf_estados,
        camada_nome="Áreas Classificadas",
        geojson_path="static/database/minas.geojson"
    )
        return render_template('mapa.html', mapa_html= map_html)