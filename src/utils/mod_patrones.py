"""
Módulo encargado de gestionar los patrones de turno utilizados por el
planificador.

Obtiene los patrones de trabajo a partir del histórico de horarios,
aplicando procesos de filtrado y generación de variantes para construir un
conjunto de patrones representativos que sirve como base para la generación
de calendarios.
"""

import pandas as pd

from config import (
    PERMITIR_VARIANTES_ENTRADA,
    PERMITIR_VARIANTES_DURACION
)


class PatronesManager:
    """
    Gestiona los patrones de turno empleados en la planificación.

    Extrae los patrones históricos de trabajo, selecciona aquellos que
    cumplen los criterios definidos por el sistema y genera variantes
    adicionales cuando la configuración del planificador lo permite,
    proporcionando un catálogo de patrones preparado para la generación de
    calendarios.
    """

    def __init__(self):

        self.patrones = None

    # =====================================
    # PATRONES HISTÓRICOS
    # =====================================

    def extraer_historicos(self):

        df = pd.read_excel(
            "data/inputs/horarios.xlsx"
        )

        df["entrada_norm"] = (

            pd.to_datetime(
                "1900-01-01 "
                +
                df["entrada"].astype(str)
            )

            .dt.round("30min")

            .dt.strftime("%H:%M")

        )

        df["duracion_norm"] = (

            (df["duracion_turno"] * 2)

            .round()

            / 2

        )

        patrones = (

            df.groupby(

                [

                    "entrada_norm",

                    "duracion_norm"

                ]

            )

            .size()

            .reset_index(
                name="frecuencia"
            )

        )

        total = (

            patrones.groupby(
                "entrada_norm"
            )["frecuencia"]

            .transform("sum")

        )

        patrones["probabilidad"] = (

            patrones["frecuencia"]

            / total

        )

        self.patrones = patrones

        return patrones

    # =====================================
    # VARIANTES
    # =====================================

    def generar_variantes(
        self,
        patrones,
        reglas
    ):

        min_horas = float(
            reglas["min_horas_dia"]
        )

        max_horas = float(
            reglas["max_horas_dias"]
        )

        registros = []

        for _, fila in patrones.iterrows():

            entrada_original = pd.to_datetime(

                fila["entrada_norm"],

                format="%H:%M"

            )

            duracion_original = float(
                fila["duracion_norm"]
            )

            if PERMITIR_VARIANTES_ENTRADA:

                desplazamientos = [

                    -90,

                    -60,

                    -30,

                    0,

                    30,

                    60,

                    90

                ]

            else:

                desplazamientos = [0]

            if PERMITIR_VARIANTES_DURACION:

                variaciones = [

                    -2,

                    -1.5,

                    -1,

                    -0.5,

                    0,

                    0.5,

                    1,

                    1.5,

                    2

                ]

            else:

                variaciones = [0]

            for desplazamiento in desplazamientos:

                nueva_entrada = (

                    entrada_original

                    +

                    pd.Timedelta(
                        minutes=desplazamiento
                    )

                )

                for variacion in variaciones:

                    nueva_duracion = (

                        duracion_original

                        +

                        variacion

                    )

                    if nueva_duracion < min_horas:

                        continue

                    if nueva_duracion > max_horas:

                        continue

                    registros.append({

                        "entrada_norm":

                            nueva_entrada.strftime(
                                "%H:%M"
                            ),

                        "duracion_norm":
                            nueva_duracion,

                        "frecuencia":
                            fila["frecuencia"],

                        "probabilidad":
                            fila["probabilidad"]

                    })

        variantes = pd.DataFrame(
            registros
        )

        variantes = variantes.drop_duplicates(

            subset=[

                "entrada_norm",

                "duracion_norm"

            ]

        )

        return variantes

    # =====================================
    # FILTRAR
    # =====================================

    def filtrar(
        self,
        patrones,
        reglas
    ):

        min_horas = int(
            reglas["min_horas_dia"]
        )

        max_horas = int(
            reglas["max_horas_dias"]
        )

        patrones = patrones[

            (

                patrones["frecuencia"] >= 5

            )

            &

            (

                patrones["probabilidad"] >= 0.05

            )

            &

            (

                patrones["duracion_norm"]

                >= min_horas

            )

            &

            (

                patrones["duracion_norm"]

                <= max_horas

            )

        ].copy()

        if (

            PERMITIR_VARIANTES_ENTRADA

            or

            PERMITIR_VARIANTES_DURACION

        ):

            patrones = self.generar_variantes(

                patrones,

                reglas

            )

        patrones = patrones.sort_values(

            [

                "entrada_norm",

                "probabilidad"

            ],

            ascending=[

                True,

                False

            ]

        )

        patrones = patrones.reset_index(
            drop=True
        )

        patrones["patron_id"] = patrones.index

        patrones = patrones[

            [

                "patron_id",

                "entrada_norm",

                "duracion_norm",

                "frecuencia",

                "probabilidad"

            ]

        ]

        self.patrones = patrones

        return patrones