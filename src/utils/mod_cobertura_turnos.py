import pandas as pd
from datetime import datetime, timedelta


def hora_a_datetime(hora):

    return datetime.strptime(
        str(hora),
        "%H:%M"
    )


def generar_cobertura_turnos(
    turnos_libres
):

    registros = []

    for _, fila in turnos_libres.iterrows():

        turno_id = fila["turno_id"]

        dia = fila["dia"]

        entrada = hora_a_datetime(
            fila["entrada"]
        )

        bloques = int(
            float(fila["duracion"]) * 2
        )

        actual = entrada

        for _ in range(bloques + 1):

            registros.append({

                "turno_id":
                    turno_id,

                "dia":
                    dia,

                "hora":
                    actual.strftime(
                        "%H:%M"
                    )

            })

            actual += timedelta(
                minutes=30
            )

    return pd.DataFrame(
        registros
    )