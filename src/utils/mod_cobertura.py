import pandas as pd
from datetime import datetime, timedelta


# =====================================
# FUNCIONES
# =====================================

def hora_a_datetime(hora):

    return datetime.strptime(
        str(hora),
        "%H:%M"
    )


# =====================================
# COBERTURA PATRONES
# =====================================

def generar_cobertura_patrones(
    patrones
):

    registros = []

    for _, fila in patrones.iterrows():

        patron_id = fila[
            "patron_id"
        ]

        entrada = hora_a_datetime(
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

                "patron_id":
                    patron_id,

                "hora":
                    actual.strftime(
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