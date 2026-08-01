"""
Módulo encargado de gestionar la configuración del planificador.

Carga las reglas y parámetros de funcionamiento definidos para el sistema de
planificación, proporcionando una interfaz unificada para acceder a la
configuración utilizada por los distintos procesos de generación y
optimización de calendarios.
"""

import pandas as pd


class SchedulerConfig:
    """
    Gestiona la configuración utilizada por el planificador.

    Centraliza la carga y acceso a las reglas de funcionamiento del sistema,
    facilitando su utilización por los distintos módulos implicados en la
    generación y evaluación de los calendarios de trabajo.
    """

    def __init__(
        self,
        fichero="data/inputs/reglas_local.xlsx"
    ):

        self.fichero = fichero

        self.reglas = None

    def cargar(self):

        df = pd.read_excel(
            self.fichero
        )

        self.reglas = dict(

            zip(

                df["parametro"],

                df["valor"]

            )

        )

        return self.reglas

    def mostrar(self):

        print("\n========================")
        print("REGLAS")
        print("========================\n")

        for k, v in self.reglas.items():

            print(
                f"{k}: {v}"
            )