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

from variables_entrada import (
    MODO_DEBUG,
    MODELO_PREDICCION
)
import pandas as pd
import numpy as np

from .mod_future_dataset import FutureDatasetBuilder
from variables_entrada import (MODO_DEBUG)

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

XGBOOST_MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "modelo_xgboost.json"
)

LSTM_MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "modelo_lstm.keras"
)

SCALER_X_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "scaler_X.pkl"
)

SCALER_Y_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "scaler_Y.pkl"
)

class CalendarPredictorLSTM:
    """
    Realiza la predicción de ventas para un periodo futuro.

    Construye el conjunto de datos correspondiente al intervalo solicitado y
    aplica el modelo de predicción de forma iterativa para estimar las ventas
    de cada hora. El resultado constituye la base para la posterior
    estimación de la demanda de personal y la generación de los horarios de
    trabajo.
    """

    def __init__(self):

        self.tipo_modelo = MODELO_PREDICCION
        self.model = None
        self.scaler_X = None
        self.scaler_y = None

        if self.tipo_modelo == "xgboost":

            from xgboost import XGBRegressor
            self.model = XGBRegressor()
            self.model.load_model(
                XGBOOST_MODEL_PATH
            )

        elif self.tipo_modelo == "lstm":

            from tensorflow.keras.models import load_model
            self.model = load_model(
                LSTM_MODEL_PATH
            )
            self.scaler_X = joblib.load(
                SCALER_X_PATH
            )
            self.scaler_y = joblib.load(
                SCALER_Y_PATH
            )

        else:

            raise ValueError(
                f"Modelo no soportado: {self.tipo_modelo}"
            )

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

        if MODO_DEBUG:
            print()
            print("========================")
            print("FUTURE DATASET CREADO")
            print("========================")
            print()

        future_dataset["ventas"] = np.nan

        historial = historico["ventas"].tolist()

        future_dataset = self._predecir_hora_a_hora(
            future_dataset,
            historial
        )

        if MODO_DEBUG:
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

            # Predicción
            future_dataset.loc[i, "ventas"] = pred

            historial.append(pred)

        return future_dataset
    
    # =====================================
    # PREDECIR
    # =====================================

    def _predecir(

        self,

        future_dataset,

        historial,

        i

    ):

        if self.tipo_modelo == "xgboost":

            return self._predecir_xgboost(

                future_dataset,

                i

            )

        elif self.tipo_modelo == "lstm":

            return self._predecir_lstm(

                future_dataset,

                historial,

                i

            )

        else:

            raise ValueError(

                f"Modelo no soportado: {self.tipo_modelo}"

            )
        
    # =====================================
    # XGBOOST
    # =====================================

    def _predecir_xgboost(

        self,

        future_dataset,

        i

    ):

        X = future_dataset.loc[
            [i],
            FEATURES
        ]

        pred = float(

            self.model.predict(
                X
            )[0]

        )

        return pred
    
    # =====================================
    # LSTM
    # =====================================

    def _predecir_lstm(
        self,
        future_dataset,
        historial,
        i
    ):

        # Últimas 24 ventas
        ventana = np.array(
            historial[-24:]
        ).reshape(-1, 1)

        # Escalar
        ventana = self.scaler_X.transform(
            ventana
        )

        # Dar formato (1, 24, 1)
        ventana = ventana.reshape(
            1,
            24,
            1
        )

        # Predicción
        pred = self.model.predict(
            ventana,
            verbose=0
        )

        # Desescalar
        pred = self.scaler_y.inverse_transform(
            pred
        )

        return float(
            pred[0][0]
        )
    
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