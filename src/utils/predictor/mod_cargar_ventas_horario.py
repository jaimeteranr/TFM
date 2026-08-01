"""
Módulo encargado de cargar la información histórica de ventas horarias.

Recupera los registros de ventas almacenados, los integra en un único
conjunto de datos y realiza las transformaciones necesarias para unificar el
formato temporal y facilitar su utilización en los modelos de predicción.
"""

import pandas as pd
from pathlib import Path


class VentasLoader:
    """
    Gestiona la carga de la información histórica de ventas horarias.

    Procesa los ficheros de ventas disponibles, unifica su contenido y
    prepara un conjunto de datos ordenado cronológicamente para su
    utilización en las distintas fases del sistema de predicción.
    """

    def __init__(
        self,
        carpeta="data/sales_hourly"
    ):

        self.carpeta = Path(carpeta)

    def cargar(self):

        archivos = sorted(
            self.carpeta.glob("*.csv")
        )

        dfs = []

        for archivo in archivos:

            df = pd.read_csv(
                archivo
            )

            dfs.append(df)

        ventas = pd.concat(

            dfs,

            ignore_index=True

        )

        # =====================================
        # FECHA Y HORA
        # =====================================

        ventas["datetime"] = pd.to_datetime(
            ventas["datetime"]
        )

        ventas["Fecha"] = (
            ventas["datetime"]
            .dt.normalize()
        )

        ventas["Hora"] = (
            ventas["datetime"]
            .dt.strftime("%H:%M")
        )

        # =====================================
        # ORDENAR
        # =====================================

        ventas = ventas.sort_values(
            "datetime"
        )

        ventas = ventas.reset_index(
            drop=True
        )

        return ventas