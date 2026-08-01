"""
Módulo encargado de seleccionar el modelo de predicción de ventas.

Actúa como interfaz entre el planificador y los distintos modelos de
predicción disponibles, delegando la generación de las ventas futuras al
modelo configurado en variables_entrada.py.
"""

from variables_entrada import MODELO_PREDICCION

from .mod_calendar_xgboost import CalendarPredictorXGBoost
from .mod_calendar_lstm import CalendarPredictorLSTM


class CalendarPredictor:
    """
    Selecciona el modelo de predicción configurado y delega en él la
    generación de las ventas futuras.
    """

    def __init__(self):

        if MODELO_PREDICCION == "xgboost":

            self.predictor = CalendarPredictorXGBoost()

        elif MODELO_PREDICCION == "lstm":

            self.predictor = CalendarPredictorLSTM()

        else:

            raise ValueError(
                f"Modelo de predicción desconocido: {MODELO_PREDICCION}"
            )

    def predecir(
        self,
        historico,
        fecha_inicio,
        fecha_fin,
        eventos
    ):

        return self.predictor.predecir(

            historico=historico,

            fecha_inicio=fecha_inicio,

            fecha_fin=fecha_fin,

            eventos=eventos

        )