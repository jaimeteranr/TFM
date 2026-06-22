import pandas as pd


def generar_turnos_libres(
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

        entrada = apertura - pd.Timedelta(
            minutes=
            reglas["minutos_montaje"]
        )

        while entrada <= cierre:

            duracion = min_horas

            # print("\n----------------")
            # print(dia)
            # print("apertura:", apertura)
            # print("cierre:", cierre)
            # print("entrada inicial:", entrada)

            # print(
            #     "probando",
            #     entrada,
            #     duracion,
            #     entrada + pd.Timedelta(hours=duracion)
            # )

            contador = 0

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

    df_debug = pd.DataFrame(registros)

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