import pandas as pd
from datetime import datetime, timedelta


class CoberturaPatronesGenerator:

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