import pandas as pd

from config import (
    PERMITIR_VARIANTES_ENTRADA,
    PERMITIR_VARIANTES_DURACION
)

# =====================================
# PATRONES HISTORICOS
# =====================================

def extraer_patrones_historicos():

    df = pd.read_excel(
        "data/inputs/horarios.xlsx"
    )

    # =========================
    # NORMALIZAR ENTRADAS
    # =========================

    df["entrada_norm"] = (

        pd.to_datetime(
            "1900-01-01 "
            +
            df["entrada"].astype(str)
        )

        .dt.round("30min")

        .dt.strftime("%H:%M")

    )

    # =========================
    # NORMALIZAR DURACION
    # =========================

    df["duracion_norm"] = (

        (df["duracion_turno"] * 2)

        .round()

        / 2

    )

    # =========================
    # FRECUENCIAS
    # =========================

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

    # =========================
    # PROBABILIDADES
    # =========================

    total_por_entrada = (

        patrones.groupby(
            "entrada_norm"
        )["frecuencia"]

        .transform("sum")

    )

    patrones["probabilidad"] = (

        patrones["frecuencia"]

        / total_por_entrada

    )

    return patrones


# =====================================
# GENERAR VARIANTES
# =====================================

def generar_variantes(
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

        # =====================
        # VARIANTES ENTRADA
        # =====================

        if PERMITIR_VARIANTES_ENTRADA:

            desplazamientos = [
                -30,
                0,
                30
            ]

        else:

            desplazamientos = [0]

        # =====================
        # VARIANTES DURACION
        # =====================

        if PERMITIR_VARIANTES_DURACION:

            variaciones_duracion = [
                -0.5,
                0,
                0.5
            ]

        else:

            variaciones_duracion = [0]

        # =====================
        # GENERAR
        # =====================

        for desplazamiento in desplazamientos:

            nueva_entrada = (

                entrada_original

                + pd.Timedelta(
                    minutes=desplazamiento
                )

            )

            for variacion in variaciones_duracion:

                nueva_duracion = (

                    duracion_original
                    + variacion

                )

                if (

                    nueva_duracion
                    < min_horas

                ):

                    continue

                if (

                    nueva_duracion
                    > max_horas

                ):

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
# FILTRAR PATRONES
# =====================================

def filtrar_patrones(
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

    # =========================
    # VARIANTES
    # =========================

    if (

        PERMITIR_VARIANTES_ENTRADA

        or

        PERMITIR_VARIANTES_DURACION

    ):

        patrones = generar_variantes(
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

    patrones["patron_id"] = (
        patrones.index
    )

    patrones = patrones[

        [
            "patron_id",
            "entrada_norm",
            "duracion_norm",
            "frecuencia",
            "probabilidad"
        ]

    ]

    return patrones