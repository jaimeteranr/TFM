"""
Módulo encargado de gestionar los horarios base de funcionamiento del
establecimiento.

Carga la configuración de apertura y cierre correspondiente a cada
temporada, proporcionando una representación unificada de los horarios de
funcionamiento utilizada por los procesos de planificación de calendarios.
"""

import pandas as pd
from variables_entrada import (MODO_DEBUG)


class HorariosBaseLoader:
    """
    Gestiona la carga de los horarios base del establecimiento.

    Obtiene la configuración de apertura y cierre asociada a cada temporada,
    adaptando la información a un formato homogéneo que facilita su
    utilización por los distintos módulos del planificador.
    """

    def __init__(self):

        self.horarios = None
        self.temporadas = None

    # =====================================
    # CARGAR HORARIOS BASE
    # =====================================

    def cargar(
        self,
        temporada
    ):

        self.horarios = pd.read_excel(
            "data/inputs/horario_base.xlsx"
        )

        self.temporadas = pd.read_excel(
            "data/inputs/temporada.xlsx"
        )

        if MODO_DEBUG: 

            print("\nDEBUG HORARIO_BASE\n")

            print(

                self.horarios[
                    [
                        "dia_semana",
                        "apertura",
                        "cierre"
                    ]
                ].head(10)

            )

            print(
                type(
                    self.horarios.iloc[0]["apertura"]
                )
            )

            print(
                type(
                    self.horarios.iloc[0]["cierre"]
                )
            )
        

        id_temporada = int(

            self.temporadas.loc[

                self.temporadas["nombre"]
                == temporada,

                "id"

            ].iloc[0]

        )

        horarios = self.horarios[

            self.horarios["id_temporada"]

            == id_temporada

        ].copy()

        dias_map = {

            "lunes": "Monday",

            "martes": "Tuesday",

            "miercoles": "Wednesday",

            "jueves": "Thursday",

            "viernes": "Friday",

            "sabado": "Saturday",

            "domingo": "Sunday"

        }

        resultado = {}

        for _, fila in horarios.iterrows():

            apertura = None
            cierre = None

            if pd.notna(fila["apertura"]):

                apertura = fila["apertura"].strftime(
                    "%H:%M"
                )

            if pd.notna(fila["cierre"]):

                cierre = fila["cierre"].strftime(
                    "%H:%M"
                )

            resultado[
                dias_map[
                    fila["dia_semana"]
                ]
            ] = {

                "abierto":
                    int(
                        fila["abierto"]
                    ),

                "apertura":
                    apertura,

                "cierre":
                    cierre

            }

        return resultado