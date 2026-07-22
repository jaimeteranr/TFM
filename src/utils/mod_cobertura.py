"""
Módulo encargado de generar la cobertura temporal asociada a los patrones de
turno.

Transforma la información de los patrones definidos en los intervalos
horarios que cubre cada uno de ellos, generando un conjunto de datos que
permite analizar y evaluar la cobertura prevista para cada patrón.
"""

import pandas as pd
from datetime import datetime, timedelta


class CoberturaPatronesGenerator:
    """
    Genera la cobertura horaria correspondiente a los patrones de turno.

    Convierte cada patrón en la secuencia de intervalos temporales que
    representa su cobertura, produciendo una estructura de datos preparada
    para su utilización en los procesos de planificación y evaluación de
    calendarios.
    """

    def __init__(
        self,
        patrones
    ):

        self.patrones = patrones

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

        for _, fila in self.patrones.iterrows():

            patron_id = fila[
                "patron_id"
            ]

            entrada = self._hora_a_datetime(
                fila["entrada_norm"]
            )

            duracion = float(
                fila["duracion_norm"]
            )

            bloques = int(
                duracion * 2
            )

            actual = entrada

            for _ in range(bloques):

                registros.append({

                    "patron_id": patron_id,

                    "hora": actual.strftime(
                        "%H:%M"
                    )

                })

                actual += timedelta(
                    minutes=30
                )

        cobertura = pd.DataFrame(
            registros
        )

        return cobertura