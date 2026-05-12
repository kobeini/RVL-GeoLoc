from flask import Flask, render_template_string, jsonify
import leafmap
import leafmap.foliumap as leaf
from controllers import routes
from IPython.display import display
from config import engine, query_lito, query_estados
import geopandas as gpd
import json
from sqlalchemy import create_engine


class Conversor:
    @staticmethod
    def postgis_to_geojson(query=None, query2=None, geom_col='wkb_geometry'):
        # Usa as queries padrão se não forem fornecidas
        if query is None:
            query = query_lito
        if query2 is None:
            query2 = query_estados

        gdf = gpd.read_postgis(query, engine, geom_col=geom_col)
        gdf2 = gpd.read_postgis(query2, engine, geom_col=geom_col)
        resultado = gpd.overlay(gdf, gdf2)
        return json.loads(resultado.to_json())

    @staticmethod
    def json_html(geojson, camada):
        m = leaf.Map()
        m.add_geojson(geojson, layer_name=camada, style={
            "fillColor": "#ff0000",  # Vermelho
            "color": "#000000",       # Borda preta
            "weight": 2,              # Espessura da borda
            "fillOpacity": 0.7        # Opacidade do preenchimento
        })
        map_html = m.to_html()
        return map_html
