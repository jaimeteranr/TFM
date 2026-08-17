"""
Módulo encargado de seleccionar el modelo de predicción de ventas.

Actúa como interfaz entre el planificador y los distintos modelos de
predicción disponibles, delegando la generación de las ventas futuras al
modelo configurado en variables_entrada.py.
"""

from pathlib import Path

from variables_entrada import (
    MODELO_PREDICCION,
    TIPO_PREDICCION
)

from .mod_calendar_xgboost import CalendarPredictorXGBoost


class CalendarPredictor:

    def __init__(self):

        self.predictor = None

    def obtener_ruta_modelo(
        self,
        fecha
    ):

        base = (
            Path(__file__).resolve().parent.parent
            / "models"
        )

        # COMPLETA

        if TIPO_PREDICCION == "completa":

            return base / "completa"

        # ESTACIONAL

        elif TIPO_PREDICCION == "estacional":

            mes = fecha.month
            dia = fecha.day

            es_verano = (
                (
                    mes > 6
                    or (
                        mes == 6
                        and dia >= 15
                    )
                )
                and
                (
                    mes < 9
                    or (
                        mes == 9
                        and dia <= 15
                    )
                )
            )

            if es_verano:

                return (
                    base
                    / "estacional"
                    / "verano"
                )

            return (
                base
                / "estacional"
                / "invierno"
            )

        # MENSUAL

        elif TIPO_PREDICCION == "mensual":

            nombres_meses = {
                1: "enero",
                2: "febrero",
                3: "marzo",
                4: "abril",
                5: "mayo",
                6: "junio",
                7: "julio",
                8: "agosto",
                9: "septiembre",
                10: "octubre",
                11: "noviembre",
                12: "diciembre"
            }

            return (
                base
                / "mensual"
                / nombres_meses[fecha.month]
            )

        else:

            raise ValueError(
                f"TIPO_PREDICCION desconocido: "
                f"{TIPO_PREDICCION}"
            )

    def predecir(
        self,
        historico,
        fecha_inicio,
        fecha_fin,
        eventos
    ):

        ruta_modelo = self.obtener_ruta_modelo(
            fecha_inicio
        )

        # =====================================
        # CREAR PREDICTOR
        # =====================================

        if MODELO_PREDICCION == "xgboost":

            self.predictor = CalendarPredictorXGBoost(
                ruta_modelo
            )

        else:

            raise ValueError(
                f"Modelo de predicción desconocido: "
                f"{MODELO_PREDICCION}"
            )

        # =====================================
        # DEBUG
        # =====================================

        print()
        print("========================")
        print("MODELO DE PREDICCIÓN")
        print("========================")
        print("Modelo:", MODELO_PREDICCION)
        print("Tipo:", TIPO_PREDICCION)
        print("Ruta:", ruta_modelo)
        print("========================")

        # =====================================
        # PREDICCIÓN
        # =====================================

        return self.predictor.predecir(

            historico=historico,

            fecha_inicio=fecha_inicio,

            fecha_fin=fecha_fin,

            eventos=eventos

        )