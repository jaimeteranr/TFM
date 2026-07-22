"""
Módulo encargado de construir el conjunto de datos futuro utilizado por los
modelos de predicción.

Genera el dataset correspondiente al periodo solicitado e integra toda la
información necesaria para realizar las predicciones, incluyendo variables
temporales, condiciones meteorológicas y eventos relevantes. El resultado es
un conjunto de datos preparado para ser utilizado por los modelos de
predicción de ventas y demanda de personal.
"""

import pandas as pd
from .mod_openmeteo import OpenMeteoLoader
from src.utils.mod_temporada import Temporada


class FutureDatasetBuilder:
    """
    Construye el dataset correspondiente al periodo para el que se desean
    realizar las predicciones.

    Coordina la generación de las variables temporales y la incorporación de
    la información meteorológica y de eventos, obteniendo un conjunto de
    datos completo que servirá como entrada a los modelos de Machine
    Learning.
    """

    def __init__(

        self,

        fecha_inicio,

        fecha_fin,

        eventos

    ):

        self.fecha_inicio = pd.to_datetime(fecha_inicio)

        self.fecha_fin = pd.to_datetime(fecha_fin)

        self.eventos = eventos


    def crear(self):

        # =====================================
        # HORAS DE APERTURA
        # =====================================
        temporada = Temporada().obtener_temporada(
            self.fecha_inicio
        )

        horas = list(range(12,24))

        horas += [0,1]

        registros = []

        fecha = self.fecha_inicio

        while fecha <= self.fecha_fin:

            for hora in horas:

                registros.append({

                    "Fecha": fecha.normalize(),

                    "hora": hora,

                    "Hora": f"{hora:02d}:00"

                })

            fecha += pd.Timedelta(days=1)

        dataset = pd.DataFrame(registros)

        dataset["Fecha_datetime"] = dataset["Fecha"]

        mask = dataset["hora"] < 12

        dataset.loc[mask, "Fecha_datetime"] = (
            dataset.loc[mask, "Fecha_datetime"] + pd.Timedelta(days=1)
        )

        dataset["datetime"] = (
            dataset["Fecha_datetime"]
            +
            pd.to_timedelta(
                dataset["hora"],
                unit="h"
            )
        )

        dataset = dataset.drop(columns="Fecha_datetime")

        dataset["año"] = dataset["datetime"].dt.year

        dataset["mes"] = dataset["datetime"].dt.month

        dataset["dia_mes"] = dataset["datetime"].dt.day

        dataset["dia_semana"] = (

            dataset["datetime"]
            .dt.dayofweek
            +1
        )

        dataset["minuto"] = dataset["datetime"].dt.minute

        dataset["temporada"] = (
            1 if temporada.lower() == "verano" else 0
        )

        dataset["dia_semana_nombre"] = (

            dataset["datetime"]

            .dt.day_name()

        )

        dataset["fin_semana"] = (

            dataset["datetime"]

            .dt.dayofweek>=5

        ).astype(int)

        dataset["hora_fin_semana"]=(

            dataset["fin_semana"]*24

            +

            dataset["hora"]

        )

        # =====================================
        # METEOROLOGÍA
        # =====================================

        weather = OpenMeteoLoader()

        meteorologia = weather.obtener(

            self.fecha_inicio.strftime("%Y-%m-%d"),

            self.fecha_fin.strftime("%Y-%m-%d")

        )

        dataset = dataset.merge(

            meteorologia[

                [
                    "Fecha",
                    "Hora",
                    "temperatura_celsius",
                    "humedad_porcentaje",
                    "lluvia_mm",
                    "nubosidad_porcentaje",
                    "viento_km_h",
                    "weather_code"
                ]

            ],

            on=[
                "Fecha",
                "Hora"
            ],

            how="left"

        )

        # =====================================
        # EVENTOS
        # =====================================

        columnas_eventos = [
            "Fecha",
            "festivo",
            "prefestivo",
            "evento",
            "evento_importancia",
            "racing",
            "hora_racing_decimal",
            "racing_tarde",
            "racing_noche"
        ]

        dataset = dataset.merge(
            self.eventos[columnas_eventos],
            on="Fecha",
            how="left"
        )

        # =====================================
        # LIMPIEZA
        # =====================================

        columnas = [

            "festivo",
            "prefestivo",
            "evento",
            "evento_importancia",
            "racing",
            "racing_tarde",
            "racing_noche",
            "hora_racing_decimal"

        ]

        for columna in columnas:

            if columna not in dataset.columns:
                dataset[columna] = 0

            dataset[columna] = dataset[columna].fillna(0)

        print()
        print("========================")
        print("FUTURE DATASET")
        print("========================")
        print()

        print(dataset.head())
        print()
        print(dataset.info())



        return dataset 