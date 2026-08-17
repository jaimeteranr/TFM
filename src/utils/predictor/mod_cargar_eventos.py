"""
Módulo encargado de cargar y preparar la información relacionada con los
eventos y el calendario.

Obtiene la información de festivos, eventos y partidos, genera las variables
derivadas necesarias y normaliza el conjunto de datos para que pueda ser
utilizado por los modelos de predicción de ventas y demanda de personal.
"""

import pandas as pd
from src.scheduler.variables_entrada import (MODO_DEBUG)


class EventosLoader:
    """
    Gestiona la carga y preparación de la información de eventos.

    Procesa el calendario de eventos, incorporando variables asociadas a
    festivos, prefestivos, partidos y otros acontecimientos relevantes,
    generando un conjunto de datos listo para su integración con el resto de
    las fuentes de información del sistema.
    """

    def __init__(
        self,
        fichero="data/inputs/calendario_eventos.xlsx"
    ):

        self.fichero = fichero

    def cargar(self):

        eventos = pd.read_excel(
            self.fichero
        )

        # =====================================
        # FECHA
        # =====================================

        eventos["Fecha"] = pd.to_datetime(
            eventos["fecha"],
            dayfirst=True
        )

        eventos = eventos.drop(
            columns="fecha"
        )

        # =====================================
        # RENOMBRAR COLUMNAS
        # =====================================

        eventos = eventos.rename(

            columns={

                "evento": "evento_importancia",

                "Unnamed: 6": "evento_nombre"

            }

        )

        # =====================================
        # HORA RACING
        # =====================================

        eventos["hora_racing"] = pd.to_datetime(

            eventos["horario_racing"],

            format="%H:%M:%S",

            errors="coerce"

        )

        eventos["hora_racing_decimal"] = (

            eventos["hora_racing"].dt.hour

            +

            eventos["hora_racing"].dt.minute / 60

        )

        # =====================================
        # VARIABLES DERIVADAS DEL RACING
        # =====================================

        eventos["racing_tarde"] = (
            (eventos["racing"] == 1)
            &
            (eventos["hora_racing_decimal"] >= 17)
        ).astype(int)

        eventos["racing_noche"] = (
            (eventos["racing"] == 1)
            &
            (eventos["hora_racing_decimal"] >= 20)
        ).astype(int)

        eventos = eventos.drop(
            columns="hora_racing"
        )

        # =====================================
        # PREFESTIVO
        # =====================================

        eventos["prefestivo"] = 0

        festivos = eventos.index[
            eventos["festivo"] == 1
        ]

        for i in festivos:

            if i > 0:

                eventos.loc[
                    i - 1,
                    "prefestivo"
                ] = 1

        # =====================================
        # FIN DE SEMANA
        # =====================================

        eventos["fin_semana"] = (
            eventos["dia_semana"] >= 6
        ).astype(int)

        # =====================================
        # HAY EVENTO
        # =====================================

        eventos["evento"] = (
            eventos["evento_importancia"] > 0
        ).astype(int)

        
        if MODO_DEBUG:
            print("\n========================")
            print("COMPROBACIÓN PREFESTIVOS")
            print("========================")

            print(
                eventos[
                    (eventos["festivo"] == 1)
                    |
                    (eventos["prefestivo"] == 1)
                ][[
                    "Fecha",
                    "festivo",
                    "prefestivo"
                ]]
            )

        return eventos