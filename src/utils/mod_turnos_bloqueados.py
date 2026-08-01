"""
Módulo encargado de gestionar los turnos bloqueados utilizados por el
planificador. Horarios de turnos fijos que no se pueden modificar y se deben respetar.

Carga la información de los turnos previamente fijados y la adapta al
formato empleado por el sistema, permitiendo que el proceso de planificación
considere asignaciones ya establecidas durante la generación de calendarios.
"""

import pandas as pd

from variables_entrada import USAR_TURNOS_BLOQUEADOS


class TurnosBloqueados:
    """
    Gestiona la carga de los turnos bloqueados del sistema. Turnos de trabajo fijos
    y que no se pueden modificar durante la planificación.

    Obtiene las asignaciones de turnos previamente definidas y las prepara
    para su utilización por el planificador, garantizando que dichas
    asignaciones sean respetadas durante el proceso de generación del
    calendario de trabajo.
    """


    def cargar_turnos_bloqueados(
        self
    ):

        if not USAR_TURNOS_BLOQUEADOS:

            return pd.DataFrame()

        try:

            df = pd.read_excel(
                "data/inputs/turnos_bloqueados.xlsx"
            )

            # =========================
            # DIA NUMÉRICO -> TEXTO
            # =========================

            mapa_dias = {

                1: "Monday",
                2: "Tuesday",
                3: "Wednesday",
                4: "Thursday",
                5: "Friday",
                6: "Saturday",
                7: "Sunday"

            }

            df["dia"] = df["dia"].map(
                mapa_dias
            )

            # =========================
            # NORMALIZAR HORA
            # =========================

            df["entrada"] = (

                df["entrada"]

                .astype(str)

                .str[:5]

            )

            return df

        except Exception as e:

            print(
                "Error cargando turnos bloqueados:",
                e
            )

            return pd.DataFrame()