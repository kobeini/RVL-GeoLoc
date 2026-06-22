import json
import os
from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional

import geopandas as gpd
import leafmap.foliumap as leafmap
from folium import FeatureGroup, GeoJson, GeoJsonPopup, LayerControl
from sqlalchemy import create_engine

from config import Config

QUERY_LITHOLOGY = (
    "select * from public.banco_lito "
    "where lower(litotipo2) like '%%carbonatito%%' "
    "or lower(litotipo1) like '%%piroxenito%%'"
)
QUERY_STATES = "select * from public.teste where nome like '%%São Paulo%%'"

BRAZIL_MAP_CENTER = (-14.0, -55.0)
BRAZIL_MAP_ZOOM = 5

_CLASSIFICATION_COLORS = {
    "Solo Compatível": "red",
    "Estado": "blue",
    "Intersecção": "purple",
}
_LITHOLOGY_STYLE = {"fillColor": "green", "color": "black", "weight": 1, "fillOpacity": 0.3}
_STATES_STYLE = {"fillColor": "orange", "color": "black", "weight": 1, "fillOpacity": 0.3}
_MINE_STYLE = {"fillColor": "yellow", "color": "black", "weight": 2, "fillOpacity": 0.5}

_STATE_FIELD_CANDIDATES = ("nome", "uf", "sigla", "estado")


@dataclass
class MapLayer:

    name: str
    geojson: dict
    style_function: Callable[[dict], dict]
    popup_fields: list = field(default_factory=list)
    popup_aliases: list = field(default_factory=list)
    visible_by_default: bool = True


class MapBuilder:

    @staticmethod
    def _resolve_overlay_columns(
        original_columns: Iterable[str],
        suffix: str,
        overlay_columns: Iterable[str],
        geom_col: str,
    ) -> list:
        overlay_columns = set(overlay_columns)
        resolved = [
            col + suffix if (col + suffix) in overlay_columns else col
            for col in original_columns
            if (col + suffix) in overlay_columns or col in overlay_columns
        ]
        if resolved:
            return resolved
        return [col for col in overlay_columns if col.endswith(suffix) and col != geom_col]

    @classmethod
    def load_layers(
        cls,
        lithology_query: Optional[str] = None,
        states_query: Optional[str] = None,
        geom_col: str = "wkb_geometry",
    ):
        """Load the lithology and states layers from PostGIS and classify
        each resulting polygon as lithology-only, state-only, or both
        (intersection).

        Returns a 3-tuple: ``(merged_gdf, lithology_gdf, states_gdf)``.
        """
        lithology_query = lithology_query or QUERY_LITHOLOGY
        states_query = states_query or QUERY_STATES
        engine = create_engine(Config.POSTGIS_DATABASE_URI)

        lithology_gdf = gpd.read_postgis(lithology_query, engine, geom_col=geom_col)
        states_gdf = gpd.read_postgis(states_query, engine, geom_col=geom_col)

        merged_gdf = gpd.overlay(lithology_gdf, states_gdf, how="union")

        lithology_columns = [c for c in lithology_gdf.columns if c != geom_col]
        states_columns = [c for c in states_gdf.columns if c != geom_col]

        resolved_lithology_cols = cls._resolve_overlay_columns(
            lithology_columns, "_1", merged_gdf.columns, geom_col
        )
        resolved_states_cols = cls._resolve_overlay_columns(
            states_columns, "_2", merged_gdf.columns, geom_col
        )

        has_lithology = (
            merged_gdf[resolved_lithology_cols].notna().any(axis=1)
            if resolved_lithology_cols
            else False
        )
        has_state = (
            merged_gdf[resolved_states_cols].notna().any(axis=1)
            if resolved_states_cols
            else False
        )

        merged_gdf["classification"] = "nenhum"
        merged_gdf.loc[has_lithology & ~has_state, "classification"] = "Solo Compatível"
        merged_gdf.loc[~has_lithology & has_state, "classification"] = "Estado"
        merged_gdf.loc[has_lithology & has_state, "classification"] = "Intersecção"

        return merged_gdf, lithology_gdf, states_gdf

    @staticmethod
    def _detect_state_field(states_gdf) -> Optional[str]:
        for candidate in _STATE_FIELD_CANDIDATES:
            if candidate in states_gdf.columns:
                return candidate
        return states_gdf.columns[0] if len(states_gdf.columns) else None

    @classmethod
    def _build_layers(cls, merged_gdf, lithology_gdf, states_gdf, layer_name, mine_geojson_paths):
        def style_by_classification(feature):
            classification = feature["properties"].get("classification", "nenhum")
            return {
                "fillColor": _CLASSIFICATION_COLORS.get(classification, "gray"),
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.6,
            }

        lithology_type_columns = [c for c in merged_gdf.columns if c.startswith("litotipo")]
        merged_popup_fields = ["classification"] + lithology_type_columns
        merged_popup_aliases = ["Tipo:"] + [
            f"Litotipo_{i + 1}:" for i in range(len(lithology_type_columns))
        ]

        state_field = cls._detect_state_field(states_gdf)

        layers = [
            MapLayer(
                name=layer_name,
                geojson=merged_gdf.to_json(),
                style_function=style_by_classification,
                popup_fields=merged_popup_fields,
                popup_aliases=merged_popup_aliases,
                visible_by_default=True,
            ),
            MapLayer(
                name="Litologia Original",
                geojson=lithology_gdf.to_json(),
                style_function=lambda _feature: _LITHOLOGY_STYLE,
                popup_fields=["litotipo1", "litotipo2"],
                popup_aliases=["Litotipo 1:", "Litotipo 2:"],
                visible_by_default=False,
            ),
            MapLayer(
                name="Estados",
                geojson=states_gdf.to_json(),
                style_function=lambda _feature: _STATES_STYLE,
                popup_fields=[state_field] if state_field else [],
                popup_aliases=["Estado:"] if state_field else [],
                visible_by_default=False,
            ),
        ]

        layers.extend(cls._build_mine_layers(mine_geojson_paths))
        return layers

    @staticmethod
    def _build_mine_layers(geojson_paths) -> list:
        """Build one MapLayer per local mine GeoJSON file that exists on disk."""
        if not geojson_paths:
            return []
        if isinstance(geojson_paths, str):
            geojson_paths = [geojson_paths]

        mine_layers = []
        for index, path in enumerate(geojson_paths):
            if not os.path.exists(path):
                print(f"Aviso: arquivo {path} não encontrado, pulando camada de minas.")
                continue
            with open(path, "r", encoding="utf-8") as geojson_file:
                geojson_data = json.load(geojson_file)
            layer_name = f"Minas {index + 1}" if len(geojson_paths) > 1 else "Minas"
            mine_layers.append(
                MapLayer(
                    name=layer_name,
                    geojson=geojson_data,
                    style_function=lambda _feature: _MINE_STYLE,
                    visible_by_default=True,
                )
            )
        return mine_layers

    @classmethod
    def build_map_html(
        cls,
        merged_gdf,
        lithology_gdf,
        states_gdf,
        layer_name: str = "Áreas Classificadas",
        mine_geojson_paths=None,
    ) -> str:
        layers = cls._build_layers(merged_gdf, lithology_gdf, states_gdf, layer_name, mine_geojson_paths)

        leaflet_map = leafmap.Map(center=BRAZIL_MAP_CENTER, zoom=BRAZIL_MAP_ZOOM)
        leaflet_map.get_root().width = "100%"
        leaflet_map.get_root().height = "100%"

        for layer in layers:
            geojson_layer = GeoJson(
                layer.geojson,
                name=layer.name,
                style_function=layer.style_function,
                popup=(
                    GeoJsonPopup(fields=layer.popup_fields, aliases=layer.popup_aliases)
                    if layer.popup_fields
                    else None
                ),
            )
            if layer.visible_by_default:
                geojson_layer.add_to(leaflet_map)
            else:
                group = FeatureGroup(name=layer.name, show=False)
                geojson_layer.add_to(group)
                group.add_to(leaflet_map)

        LayerControl().add_to(leaflet_map)
        return leaflet_map._repr_html_()
