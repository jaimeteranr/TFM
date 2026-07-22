"""
Módulo encargado de cargar la información histórica de ventas diarias.

Recupera los registros de ventas almacenados, los integra en un único
conjunto de datos y realiza las transformaciones necesarias para unificar el
formato de las fechas y facilitar su utilización en los modelos de
predicción.
"""

import pandas as pd
from pathlib import Path


class VentasLoader:
    """
    Gestiona la carga de la información histórica de ventas diarias.

    Procesa los ficheros de ventas disponibles, unifica su contenido y
    prepara un conjunto de datos ordenado cronológicamente para su
    utilización en las distintas fases del sistema de predicción.
    """

    def __init__(
        self,
        carpeta="data/sales"
    ):

        self.carpeta = Path(carpeta)

    def cargar(self):

        archivos = sorted(
            self.carpeta.glob("*.xlsx")
        )

        dfs = []

        for archivo in archivos:

            df = pd.read_excel(archivo)

            dfs.append(df)

        ventas = pd.concat(
            dfs,
            ignore_index=True
        )

        ventas["Fecha"] = pd.to_datetime(
            ventas["Fecha"],
            format="%d/%m/%Y"
        )

        ventas = ventas.sort_values(
            "Fecha"
        ).reset_index(drop=True)

        return ventas