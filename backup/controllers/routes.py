from flask import Flask, render_template_string, redirect, url_for
from config import query_lito, query_estados
from controllers.db_conversor import Conversor
import leafmap.foliumap as leaf

app = Flask(__name__)


def init_app(app):

    @app.route('/')
    def index():
        return redirect(url_for('mapa'))

    @app.route('/mapa')
    def mapa():
        geojson_lito = Conversor.postgis_to_geojson()
        map_html = Conversor.json_html(geojson_lito, camada="Camada")
        return render_template_string(map_html)
