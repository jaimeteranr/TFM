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


MODEL_PATH = Path(__file__).resolve().parent / "modelo_xgboost.pkl"


class SalesPredictor:
    """
    Realiza la predicción de ventas a partir de un modelo entrenado.

    Aplica el modelo de Machine Learning sobre un conjunto de datos con las
    variables de entrada necesarias y devuelve el mismo dataset enriquecido
    con las ventas estimadas para cada intervalo temporal.
    """

    def __init__(self):

        self.model = joblib.load(MODEL_PATH)

    def predecir(
        self,
        dataset: pd.DataFrame
    ):

        dataset = dataset.copy()

        dataset["ventas"] = self.model.predict(
            dataset[ModelBase.FEATURES]
        )

        return dataset