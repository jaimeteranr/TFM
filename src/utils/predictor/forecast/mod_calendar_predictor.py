"""
Módulo encargado de predecir las ventas futuras del establecimiento.

Utiliza un modelo de Machine Learning previamente entrenado para estimar las
ventas de cada intervalo horario del periodo solicitado. La predicción se
realiza de forma secuencial, incorporando cada nuevo valor estimado al
histórico para generar las variables temporales necesarias en las horas
posteriores.
"""

from pathlib import Path

import joblib
import pandas as pd
import numpy as np

from .mod_future_dataset import FutureDatasetBuilder

FEATURES = [
            "temperatura_celsius",
            "humedad_porcentaje",
            "lluvia_mm",
            "nubosidad_porcentaje",
            "viento_km_h",
            "weather_code",
            "hora",
            "dia_semana",
            "festivo",
            "prefestivo",
            "fin_semana",
            "evento",
            "evento_importancia",
            "racing",
            "hora_racing_decimal",
            "racing_tarde",
            "racing_noche",
            "hora_fin_semana",
            "ventas_lag_1h",
            "ventas_lag_2h",
            "ventas_lag_24h",
            "ventas_lag_168h",
            "ventas_media_3h",
            "ventas_media_24h"
        ]

class CalendarPredictor:
    """
    Realiza la predicción de ventas para un periodo futuro.

    Construye el conjunto de datos correspondiente al intervalo solicitado y
    aplica el modelo de predicción de forma iterativa para estimar las ventas
    de cada hora. El resultado constituye la base para la posterior
    estimación de la demanda de personal y la generación de los horarios de
    trabajo.
    """

    def __init__(self):

        ruta_modelo = (
            Path(__file__).resolve().parent.parent
            / "models"
            / "modelo_xgboost.pkl"
        )

        self.model = joblib.load(ruta_modelo)

    def predecir(
        self,
        historico,
        fecha_inicio,
        fecha_fin,
        eventos
    ):

        future_dataset = FutureDatasetBuilder(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            eventos=eventos
        ).crear()

        print("1 - FutureDataset creado")

        future_dataset["ventas"] = np.nan

        historial = historico["ventas"].tolist()

        future_dataset = self._predecir_hora_a_hora(
            future_dataset,
            historial
        )

        print(type(future_dataset))

        return future_dataset
    
    def _predecir_hora_a_hora(
        self,
        future_dataset,
        historial
    ):

        for i in future_dataset.index:

            # Calcular variables históricas
            lags = self._calcular_lags(historial)

            # Escribirlas en la fila actual
            for nombre, valor in lags.items():
                future_dataset.loc[i, nombre] = valor

            # Construir el vector de entrada
            X = future_dataset.loc[[i], FEATURES]

            # Predicción
            pred = float(self.model.predict(X)[0])

            # Guardar la predicción
            future_dataset.loc[i, "ventas"] = pred

            # Añadir al historial para las siguientes horas
            historial.append(pred)

        return future_dataset
            
    def _calcular_lags(self, historial):

        if len(historial) < 98:
            raise ValueError(
                f"Se necesitan al menos 98 registros históricos y hay {len(historial)}."
            )

        return {

            "ventas_lag_1h": historial[-1],

            "ventas_lag_2h": historial[-2],

            "ventas_lag_24h": historial[-14],

            "ventas_lag_168h": historial[-98],

            "ventas_media_3h": sum(historial[-3:]) / 3,

            "ventas_media_24h": sum(historial[-14:]) / 14

        }