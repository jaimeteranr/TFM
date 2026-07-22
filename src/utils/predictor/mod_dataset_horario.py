"""
Módulo encargado de construir el conjunto de datos horario utilizado para el
entrenamiento del modelo de predicción de ventas.

Integra la información de ventas, meteorología y eventos, generando las
variables temporales e históricas necesarias para obtener un dataset
completo preparado para el entrenamiento y evaluación de los modelos de
Machine Learning.
"""

import pandas as pd


class DatasetBuilder:
    """
    Construye el dataset horario para el entrenamiento del modelo de ventas.

    Coordina la integración de las distintas fuentes de información,
    incorporando variables temporales y características derivadas del
    histórico de ventas para generar un conjunto de datos preparado para el
    entrenamiento de los modelos de predicción.
    """

    def __init__(
        self,
        ventas,
        meteorologia,
        eventos
    ):

        self.ventas = ventas
        self.meteorologia = meteorologia
        self.eventos = eventos

    def crear(self):

        print("\nVENTAS:", len(self.ventas))
        print("METEOROLOGÍA:", len(self.meteorologia))
        print("EVENTOS:", len(self.eventos))

        # ==========================
        # UNIÓN VENTAS + METEOROLOGÍA
        # ==========================

        dataset = self.ventas.merge(

            self.meteorologia,

            on=[
                "Fecha",
                "Hora"
            ],

            how="inner"

        )

        print("\nTras merge ventas + meteorología:", len(dataset))

        # ==========================
        # UNIÓN EVENTOS
        # ==========================

        dataset = dataset.merge(

            self.eventos,

            on="Fecha",

            how="left"

        )

        print("Tras merge eventos:", len(dataset))

        # =====================================
        # VARIABLES TEMPORALES
        # =====================================

        dataset["año"] = dataset["datetime"].dt.year

        dataset["mes"] = dataset["datetime"].dt.month

        dataset["dia_mes"] = dataset["datetime"].dt.day

        dataset["hora"] = dataset["datetime"].dt.hour

        dataset["minuto"] = dataset["datetime"].dt.minute

        dataset["dia_semana_nombre"] = dataset["datetime"].dt.day_name()

        dataset["fin_semana"] = (

            dataset["datetime"]

            .dt.dayofweek >= 5

        ).astype(int)

        # =====================================
        # INTERACCIÓN HORA + FIN DE SEMANA (0-23 entre semana y 24-48 fin de semana)
        # =====================================

        dataset["hora_fin_semana"] = (

            dataset["hora"]

            +

            24 * dataset["fin_semana"]

        )
        print("Tras variables temporales:", len(dataset))

        # =====================================
        # ORDENAR
        # =====================================

        dataset = dataset.sort_values(
            "datetime"
        )

        dataset = dataset.reset_index(
            drop=True
        )

        # =====================================
        # CONFIGURACIÓN TEMPORAL
        # =====================================

        HORAS_DIA = 14
        HORAS_SEMANA = HORAS_DIA * 7

        # =====================================
        # VARIABLES HISTÓRICAS
        # =====================================

        dataset["ventas_lag_1h"] = (
            dataset["ventas"].shift(1)
        )

        dataset["ventas_lag_2h"] = (
            dataset["ventas"].shift(2)
        )

        # Misma hora del día anterior
        dataset["ventas_lag_24h"] = (
            dataset["ventas"].shift(HORAS_DIA)
        )

        # Misma hora de la semana anterior
        dataset["ventas_lag_168h"] = (
            dataset["ventas"].shift(HORAS_SEMANA)
        )

        # Promedio de las tres últimas horas abiertas
        dataset["ventas_media_3h"] = (
            dataset["ventas"]
            .rolling(window=3, min_periods=3)
            .mean()
            .shift(1)
        )

        # Promedio del día anterior completo (14 horas abiertas)
        dataset["ventas_media_24h"] = (
            dataset["ventas"]
            .rolling(window=HORAS_DIA, min_periods=HORAS_DIA)
            .mean()
            .shift(1)
        )

        print("Tras crear lags:", len(dataset))

        # =====================================
        # LIMPIEZA
        # =====================================

        dataset = dataset.drop(

            columns=[

                "index",

                "horario_racing",

                "evento_nombre"

            ],

            errors="ignore"

        )

        print("\nNulos por columna:")

        print(

            dataset[
                [
                    "ventas_lag_1h",
                    "ventas_lag_2h",
                    "ventas_lag_24h",
                    "ventas_lag_168h",
                    "ventas_media_3h",
                    "ventas_media_24h"
                ]
            ].isna().sum()

        )

        # =====================================
        # RELLENAR VARIABLES OPCIONALES
        # =====================================

        dataset["hora_racing_decimal"] = (

            dataset["hora_racing_decimal"]

            .fillna(-1)

        )

        # =====================================
        # ELIMINAR SOLO NAN DE LAGS
        # =====================================

        columnas_lags = [

            "ventas_lag_1h",

            "ventas_lag_2h",

            "ventas_lag_24h",

            "ventas_lag_168h",

            "ventas_media_3h",

            "ventas_media_24h"

        ]

        dataset = dataset.dropna(

            subset=columnas_lags

        ).reset_index(
            drop=True
        )

        print("\nTras dropna:", len(dataset))


        return dataset