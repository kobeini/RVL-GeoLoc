# db_conversor.py (versão corrigida)
from flask import Flask, render_template_string, jsonify
from config import engine, query_lito, query_estados
import geopandas as gpd
import folium

class Conversor:
    @staticmethod
    def postgis_to_gdf(query_estatigrafia=None, query_estado=None, geom_col='wkb_geometry'):
        if query_estatigrafia is None:
            query_estatigrafia = query_lito
        if query_estado is None:
            query_estado = query_estados

        gdf_estatigrafia = gpd.read_postgis(query_estatigrafia, engine, geom_col=geom_col)
        gdf_estado = gpd.read_postgis(query_estado, engine, geom_col=geom_col)

        uniao = gpd.overlay(gdf_estatigrafia, gdf_estado, how='union')

        cols_estati_orig = [coluna for coluna in gdf_estatigrafia.columns if coluna != geom_col]
        cols_estado_orig = [coluna for coluna in gdf_estado.columns if coluna != geom_col]

        def mapear_colunas(cols_orig, sufixo):
            mapeadas = []
            for col in cols_orig:
                if col + sufixo in uniao.columns:
                    mapeadas.append(col + sufixo)
                elif col in uniao.columns:
                    mapeadas.append(col)
            return mapeadas

        cols_estati = mapear_colunas(cols_estati_orig, '_1')
        cols_estado = mapear_colunas(cols_estado_orig, '_2')

        if not cols_estati:
            cols_estati = [coluna for coluna in uniao.columns if coluna.endswith('_1') and coluna != geom_col]
        if not cols_estado:
            cols_estado = [coluna for coluna in uniao.columns if coluna.endswith('_2') and coluna != geom_col]

        uniao['solo'] = False
        uniao['estado'] = False

        if cols_estati:
            uniao['solo'] = uniao[cols_estati].notna().any(axis=1)
        if cols_estado:
            uniao['estado'] = uniao[cols_estado].notna().any(axis=1)

        uniao['tipo'] = 'nenhum'
        uniao.loc[uniao['solo'] & ~uniao['estado'], 'tipo'] = 'Solo Compatível'
        uniao.loc[~uniao['solo'] & uniao['estado'], 'tipo'] = 'Estado'
        uniao.loc[uniao['solo'] & uniao['estado'], 'tipo'] = 'intersecao'

        uniao = uniao.drop(columns=['solo', 'estado'])
        return uniao

    @staticmethod
    def gdf_to_html(gdf, camada_nome):
        cores = {
            'Solo Compatível': 'red',
            'Estado': 'blue',
            'intersecao': 'purple'
        }

        def style_function(feature):
            tipo = feature['properties'].get('tipo', 'nenhum')
            return {
                'fillColor': cores.get(tipo, 'gray'),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.6
            }

        # Descobrir os nomes reais das colunas litotipo1 e litotipo2 no gdf
        colunas_litologia = [col for col in gdf.columns if col.startswith('litotipo')]
        campos_popup = ['tipo'] + colunas_litologia
        mapa = folium.Map(location=[-14.0, -55.0], zoom_start=5)
        folium.GeoJson(
            gdf.to_json(),
            name=camada_nome,
            style_function=style_function, popup=folium.GeoJsonPopup(
            fields=campos_popup,
            aliases=['Tipo:'] + [f'Litotipo_{i+1}:' for i in range(len(colunas_litologia))]
        )
        ).add_to(mapa)

        folium.LayerControl().add_to(mapa)
        return mapa._repr_html_()