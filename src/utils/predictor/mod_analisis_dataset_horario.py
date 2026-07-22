"""
Módulo encargado del análisis exploratorio del conjunto de datos.

Proporciona un conjunto de herramientas para examinar las características
del dataset, evaluar su calidad, identificar relaciones entre variables y
obtener estadísticas descriptivas que facilitan la comprensión del
comportamiento de las ventas y de los factores que las condicionan.
"""

import pandas as pd
import numpy as np


class DatasetAnalyzer:
    """
    Realiza el análisis exploratorio del conjunto de datos.

    Genera información descriptiva, analiza la calidad de los datos y
    estudia la relación entre las variables del dataset mediante diferentes
    indicadores estadísticos, proporcionando una visión general del
    comportamiento de la información antes del entrenamiento de los modelos.
    """

    def __init__(
        self,
        dataset
    ):

        self.dataset = dataset

    def analizar(self):

        dataset = self.dataset

        # =====================================
        # INFORMACIÓN GENERAL
        # =====================================

        print()

        print("========================")
        print("ANÁLISIS DATASET")
        print("========================")

        print()

        print("Número de registros:")

        print(len(dataset))

        print()

        print("Fechas:")

        print(

            dataset["datetime"].min(),

            "->",

            dataset["datetime"].max()

        )

        print()

        print(dataset.info())

        print()

        print(dataset.describe())

        # =====================================
        # VALORES NULOS
        # =====================================

        print()

        print("========================")
        print("VALORES NULOS")
        print("========================")

        print()

        print(dataset.isnull().sum())

        # =====================================
        # CORRELACIONES
        # =====================================

        print()

        print("========================")
        print("CORRELACIONES")
        print("========================")

        correlaciones = dataset.corr(
            numeric_only=True
        )

        print()

        print(correlaciones)

        # =====================================
        # IMPORTANCIA VENTAS
        # =====================================

        print()

        print("========================")
        print("IMPORTANCIA VENTAS")
        print("========================")

        corr = correlaciones[
            "ventas"
        ].drop(
            "ventas"
        )

        corr = corr.reindex(

            corr.abs().sort_values(
                ascending=False
            ).index

        )

        print()

        print(corr)

        # =====================================
        # PEOR HORA
        # =====================================

        print()

        print("========================")
        print("PEOR HORA")
        print("========================")

        print()

        print(

            dataset.loc[
                dataset["ventas"].idxmin()
            ]

        )

        # =====================================
        # LLUVIA
        # =====================================

        print()

        print("========================")
        print("VENTAS SEGÚN LLUVIA")
        print("========================")

        print()

        dataset["llovio"] = (
            dataset["lluvia_mm"] > 0
        ).astype(int)

        print(

            dataset.groupby(
                "llovio"
            )[[
                "ventas"
            ]].mean()

        )

        # =====================================
        # WEATHER CODE
        # =====================================

        print()

        print("========================")
        print("WEATHER CODE")
        print("========================")

        print()

        print(

            dataset.groupby(
                "weather_code"
            )[[
                "ventas"
            ]].mean()

        )

        # =====================================
        # DÍA DE LA SEMANA
        # =====================================

        print()

        print("========================")
        print("DÍA DE LA SEMANA")
        print("========================")

        print()

        print(

            dataset.groupby(
                "dia_semana_nombre"
            )[[
                "ventas"
            ]].mean()

        )

        # =====================================
        # HORA DEL DÍA
        # =====================================

        print()

        print("========================")
        print("HORA DEL DÍA")
        print("========================")

        print()

        print(

            dataset.groupby(
                "hora"
            )[[
                "ventas"
            ]].mean()

        )

        # =====================================
        # TEMPERATURA
        # =====================================

        print()

        print("========================")
        print("TEMPERATURA")
        print("========================")

        print()

        print(

            dataset[[
                "temperatura_celsius",
                "ventas"
            ]].corr()

        )