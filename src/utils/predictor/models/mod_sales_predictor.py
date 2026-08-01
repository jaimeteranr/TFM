"""
Módulo encargado de realizar la predicción de ventas utilizando un modelo
previamente entrenado.

Carga el modelo almacenado y aplica las predicciones sobre un conjunto de
datos preparado, incorporando las ventas estimadas que servirán como entrada
para las siguientes etapas del proceso de planificación.
"""

from pathlib import Path

import joblib
import pandas as pd

from models.mod_model_base import ModelBase
from variables_entrada import MODELO_PREDICCION


XGBOOST_MODEL_PATH = (
    Path(__file__).resolve().parent / "modelo_xgboost.json"
)

RED_NEURONAL_MODEL_PATH = (
    Path(__file__).resolve().parent / "modelo_red_neuronal.keras"
)

SCALER_X_PATH = (
    Path(__file__).resolve().parent / "scaler_X.pkl"
)

SCALER_Y_PATH = (
    Path(__file__).resolve().parent / "scaler_y.pkl"
)


class SalesPredictor:
    """
    Realiza la predicción de ventas a partir de un modelo entrenado.

    Aplica el modelo de Machine Learning sobre un conjunto de datos con las
    variables de entrada necesarias y devuelve el mismo dataset enriquecido
    con las ventas estimadas para cada intervalo temporal.
    """

    def __init__(self):

        self.tipo_modelo = MODELO_PREDICCION

        if self.tipo_modelo == "xgboost":

            from xgboost import XGBRegressor
            self.model = XGBRegressor()
            self.model.load_model(XGBOOST_MODEL_PATH)

        elif self.tipo_modelo == "red_neuronal":

            from tensorflow.keras.models import load_model
            self.model = load_model(RED_NEURONAL_MODEL_PATH)
            self.scaler_X = joblib.load(SCALER_X_PATH)
            self.scaler_Y = joblib.load(SCALER_Y_PATH)

        else:

            raise ValueError(
                f"Modelo desconocido: {MODELO_PREDICCION}"
            )

    def predecir(
        self,
        dataset: pd.DataFrame
    ):

        dataset = dataset.copy()

        X = dataset[ModelBase.FEATURES]

        if MODELO_PREDICCION == "xgboost":

            pred = self.model.predict(X)

        elif MODELO_PREDICCION == "red_neuronal":

            X = self.scaler_X.transform(X)

            pred = self.model.predict(X)

            pred = self.scaler_Y.inverse_transform(pred)

            pred = pred.ravel()

        dataset["ventas"] = pred

        return dataset