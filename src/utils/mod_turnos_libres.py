"""
Módulo encargado de generar el catálogo de turnos libres utilizado por el
planificador. Todos los turnos posibles.

Construye el conjunto de turnos candidatos a partir de los horarios de
apertura del establecimiento y de las reglas de planificación definidas por
el sistema, proporcionando las alternativas que podrán ser asignadas durante
el proceso de optimización.
"""

import pandas as pd


class TurnosLibres:
    """
    Genera los turnos candidatos para la planificación.

    Construye un catálogo de turnos compatibles con los horarios de
    funcionamiento y las restricciones de duración establecidas por el
    sistema, proporcionando al planificador el conjunto de alternativas
    disponibles para la asignación de trabajadores.
    """

    def generar_turnos_libres(
        self,
        horarios_base,
        reglas
    ):

        registros = []

        turno_id = 0

        min_horas = reglas[
            "min_horas_dia"
        ]

        max_horas = reglas[
            "max_horas_dias"
        ]

        for dia, info in horarios_base.items():

            print("\nHORARIO LEIDO")

            print(
                dia,
                info["apertura"],
                info["cierre"]
            )

            if not info["abierto"]:

                continue

            apertura = pd.to_datetime(
                info["apertura"],
                format="%H:%M"
            )

            cierre = pd.to_datetime(
                info["cierre"],
                format="%H:%M"
            )

            if cierre <= apertura:

                cierre += pd.Timedelta(
                    days=1
                )

            cierre_real = (

                cierre

                +

                pd.Timedelta(
                    minutes=reglas[
                        "minutos_recogida"
                    ]
                )

            )

            entrada = (

                apertura

                -

                pd.Timedelta(
                    minutes=reglas[
                        "minutos_montaje"
                    ]
                )

            )

            while entrada <= cierre:

                duracion = min_horas

                while duracion <= max_horas:

                    salida = (

                        entrada

                        +

                        pd.Timedelta(
                            hours=duracion
                        )

                    )

                    if salida <= cierre_real:

                        registros.append({

                            "turno_id":
                            turno_id,

                            "dia":
                            dia,

                            "entrada":
                            entrada.strftime(
                                "%H:%M"
                            ),

                            "duracion":
                            duracion,

                            "salida":
                            salida.strftime(
                                "%H:%M"
                            )

                        })

                        turno_id += 1

                    duracion += 0.5

                entrada += pd.Timedelta(
                    minutes=30
                )

            print(
                "TURNOS GENERADOS:",
                len(registros)
            )

        df_debug = pd.DataFrame(
            registros
        )

        print(
            "SALIDA MAXIMA:",
            df_debug["salida"].max()
        )

        return pd.DataFrame(

            registros,

            columns=[

                "turno_id",
                "dia",
                "entrada",
                "duracion",
                "salida"

            ]

        )