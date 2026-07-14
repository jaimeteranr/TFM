import pandas as pd
import numpy as np


class DatasetAnalyzer:

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

            dataset["Fecha"].min(),

            "->",

            dataset["Fecha"].max()

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
        # IMPORTANCIA BENEFICIO
        # =====================================

        print()

        print("========================")
        print("IMPORTANCIA BENEFICIO")
        print("========================")

        corr = correlaciones[
            "Beneficio"
        ].drop(
            "Beneficio"
        )

        corr = corr.reindex(

            corr.abs().sort_values(
                ascending=False
            ).index

        )

        print()

        print(corr)

        # =====================================
        # IMPORTANCIA CANTIDAD
        # =====================================

        print()

        print("========================")
        print("IMPORTANCIA CANTIDAD")
        print("========================")

        corr = correlaciones[
            "Cantidad"
        ].drop(
            "Cantidad"
        )

        corr = corr.reindex(

            corr.abs().sort_values(
                ascending=False
            ).index

        )

        print()

        print(corr)

        # =====================================
        # PEOR DÍA
        # =====================================

        print()

        print("========================")
        print("PEOR DÍA")
        print("========================")

        print()

        print(

            dataset.loc[
                dataset["Beneficio"].idxmin()
            ]

        )

        # =====================================
        # LLUVIA
        # =====================================

        print()

        print("========================")
        print("VENTAS CON / SIN LLUVIA")
        print("========================")

        print()

        print(

            dataset.groupby(
                "llovio"
            )[[
                "Beneficio",
                "Cantidad"
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
                "Beneficio",
                "Cantidad"
            ]].mean()

        )

        # =====================================
        # DÍA DE LA SEMANA
        # =====================================

        dataset["dia_semana"] = dataset[
            "Fecha"
        ].dt.day_name()

        print()

        print("========================")
        print("DÍA DE LA SEMANA")
        print("========================")

        print()

        print(

            dataset.groupby(
                "dia_semana"
            )[[
                "Beneficio",
                "Cantidad"
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
                "temp_media",
                "temp_max",
                "temp_min",
                "Beneficio"
            ]].corr()
        )