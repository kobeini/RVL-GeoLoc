# db_conversor.py (versão final com geojsons e camadas ocultas)
from flask import Flask, render_template_string, jsonify
from config import engine, query_lito, query_estados, url_database
import geopandas as gpd
import folium
import json
import os


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
        return uniao, gdf_estatigrafia, gdf_estado

    @staticmethod
    def gdf_to_html(gdf_uniao, gdf_estatigrafia, gdf_estado, camada_nome="Camada Única",
                geojson_path=None):
        cores_tipo = {'Solo Compatível': 'red', 'Estado': 'blue', 'intersecao': 'purple'}
        estilo_lito = {'fillColor': 'green', 'color': 'black', 'weight': 1, 'fillOpacity': 0.3}
        estilo_estados = {'fillColor': 'orange', 'color': 'black', 'weight': 1, 'fillOpacity': 0.3}
        estilo_geojson = {'fillColor': 'yellow', 'color': 'black', 'weight': 2, 'fillOpacity': 0.5}

        def style_uniao(feature):
            tipo = feature['properties'].get('tipo', 'nenhum')
            return {'fillColor': cores_tipo.get(tipo, 'gray'), 'color': 'black', 'weight': 1, 'fillOpacity': 0.6}

        colunas_litologia = [col for col in gdf_uniao.columns if col.startswith('litotipo')]
        campos_popup_uniao = ['tipo'] + colunas_litologia
        aliases_popup_uniao = ['Tipo:'] + [f'Litotipo_{i+1}:' for i in range(len(colunas_litologia))]

        campo_estado = None
        for possivel in ['nome', 'uf', 'sigla', 'estado']:
            if possivel in gdf_estado.columns:
                campo_estado = possivel
                break
        if campo_estado is None and len(gdf_estado.columns) > 0:
            campo_estado = gdf_estado.columns[0]


        camadas_config = [
            (gdf_uniao.to_json(), camada_nome, style_uniao,
            campos_popup_uniao, aliases_popup_uniao, True),
            (gdf_estatigrafia.to_json(), 'Litologia Original',
            lambda x: estilo_lito, ['litotipo1', 'litotipo2'],
            ['Litotipo 1:', 'Litotipo 2:'], False),
            (gdf_estado.to_json(), 'Estados',
            lambda x: estilo_estados,
            [campo_estado] if campo_estado else [],
            ['Estado:'] if campo_estado else [], False),
        ]

        if geojson_path is not None:
            if isinstance(geojson_path, str):
                geojson_path = [geojson_path]
            for idx, path in enumerate(geojson_path):
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        geojson_data = json.load(f)
                    nome_camada = f"Minas {idx+1}" if len(geojson_path) > 1 else "Minas"
                    camadas_config.append(
                        (geojson_data, nome_camada,
                         lambda x: estilo_geojson, [], [], True)
                    )
                else:
                    print(f"Arquivo {path} não encontrado, pulando...")

        mapa = folium.Map(location=[-14.0, -55.0], zoom_start=5)
        mapa.get_root().width = "100%"
        mapa.get_root().height = "100%"
        for dados, nome, estilo, campos, aliases, show_inicial in camadas_config:
            camada = folium.GeoJson(
                dados,
                name=nome,
                style_function=estilo,
                popup=folium.GeoJsonPopup(fields=campos, aliases=aliases) if campos else None
            )
            if not show_inicial:
                grupo = folium.FeatureGroup(name=nome, show=False)
                camada.add_to(grupo)
                grupo.add_to(mapa)
            else:
                camada.add_to(mapa)

        folium.LayerControl().add_to(mapa)
        return mapa._repr_html_()