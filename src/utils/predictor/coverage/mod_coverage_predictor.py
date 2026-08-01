"""
Módulo encargado de predecir la demanda de personal a partir de un conjunto
de variables operativas y contextuales.

Utiliza un modelo de Machine Learning previamente entrenado para estimar el
número de trabajadores necesarios en cada intervalo horario. Las
predicciones obtenidas constituyen la demanda de personal que posteriormente
será utilizada por el optimizador para generar los horarios de trabajo.
"""

import joblib
import numpy as np


class CoveragePredictor:
    """
    Realiza la predicción de la demanda de personal.

    Carga el modelo de cobertura entrenado y estima el número de empleados
    necesarios para cada registro del dataset de entrada, devolviendo el
    mismo conjunto de datos enriquecido con la predicción de personal.
    """

    FEATURES = [

        "ventas",

        "temperatura_celsius",
        "humedad_porcentaje",
        "lluvia_mm",
        "nubosidad_porcentaje",
        "viento_km_h",
        "weather_code",

        "hora",
        "minuto",
        "dia_semana",
        "mes",
        "dia_mes",
        "fin_semana",

        "temporada",

        "festivo",
        "prefestivo",

        "evento",
        "evento_importancia",

        "racing",
        "hora_racing_decimal",
        "racing_tarde",
        "racing_noche"

    ]

    def __init__(self):

        self.model = joblib.load(
            "modelo_cobertura.pkl"
        )

    def predecir(
        self,
        dataset
    ):

        dataset = dataset.copy()

        pred = self.model.predict(

            dataset[self.FEATURES]

        )

        dataset["personas"] = (

            np.round(pred)

            .astype(int)

        )

        dataset["personas"] = (

            dataset["personas"]

            .clip(lower=1)

        )

        return dataset