"""
Módulo encargado de generar la cobertura temporal asociada a los turnos de
trabajo.

Transforma la información de los turnos definidos en los intervalos horarios
que cubre cada uno de ellos, generando un conjunto de datos que permite
analizar y evaluar la cobertura de personal a lo largo de la planificación.
"""

import pandas as pd
from datetime import datetime, timedelta


class CoberturaTurnosGenerator:
    """
    Genera la cobertura horaria correspondiente a los turnos de trabajo.

    Convierte cada turno en la secuencia de intervalos temporales que
    representa su cobertura efectiva, produciendo una estructura de datos
    preparada para su utilización en los procesos de análisis y evaluación
    de calendarios.
    """

    def __init__(
        self,
        turnos_libres
    ):

        self.turnos_libres = turnos_libres

    def _hora_a_datetime(
        self,
        hora
    ):

        return datetime.strptime(
            str(hora),
            "%H:%M"
        )

    def generar(self):

        registros = []

        for _, fila in self.turnos_libres.iterrows():

            turno_id = fila["turno_id"]

            dia = fila["dia"]

            entrada = self._hora_a_datetime(
                fila["entrada"]
            )

            bloques = int(
                float(fila["duracion"]) * 2
            )

            actual = entrada

            for _ in range(bloques + 1):

                registros.append({

                    "turno_id": turno_id,

                    "dia": dia,

                    "hora": actual.strftime(
                        "%H:%M"
                    )

                })

                actual += timedelta(
                    minutes=30
                )

        return pd.DataFrame(
            registros
        )