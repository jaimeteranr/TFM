import pandas as pd
from datetime import datetime, timedelta


class CoberturaTurnosGenerator:

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