import pandas as pd
from datetime import timedelta


def asignar_temporada(fecha, temporadas):

    fecha_md = (
        fecha.month,
        fecha.day
    )

    for _, fila in temporadas.iterrows():

        inicio = pd.to_datetime(
            fila["fecha_inicio"],
            dayfirst=True
        )

        fin = pd.to_datetime(
            fila["fecha_fin"],
            dayfirst=True
        )

        inicio_md = (
            inicio.month,
            inicio.day
        )

        fin_md = (
            fin.month,
            fin.day
        )

        # temporada normal
        if inicio_md <= fin_md:

            if (
                inicio_md
                <= fecha_md
                <= fin_md
            ):

                return fila["nombre"]

        # temporada que cruza año
        else:

            if (
                fecha_md >= inicio_md
                or
                fecha_md <= fin_md
            ):

                return fila["nombre"]

    return None


def extraer_demanda(temporada):

    # =====================================
    # CARGA
    # =====================================

    df = pd.read_excel(
        "data/inputs/horarios.xlsx"
    )

    temporadas = pd.read_excel(
        "data/inputs/temporada.xlsx"
    )

    # =====================================
    # FECHAS
    # =====================================

    df["fecha"] = pd.to_datetime(
        df["fecha"]
    )

    df["temporada"] = df[
        "fecha"
    ].apply(
        lambda x:
        asignar_temporada(
            x,
            temporadas
        )
    )

    # Filtrar temporada solicitada

    df = df[
        df["temporada"]
        == temporada
    ].copy()

    # =====================================
    # NORMALIZAR TURNOS
    # =====================================

    df["entrada_norm"] = (
        pd.to_datetime(
            "1900-01-01 "
            +
            df["entrada"].astype(str)
        )
        .dt.round("30min")
    )

    df["duracion_norm"] = (
        (df["duracion_turno"] * 2)
        .round()
        / 2
    )

    # =====================================
    # EXPANDIR TURNOS
    # =====================================

    registros = []

    for _, row in df.iterrows():

        inicio = row["entrada_norm"]

        fin = inicio + pd.Timedelta(
            hours=row["duracion_norm"]
        )

        instante = inicio

        while instante < fin:

            registros.append({

                "fecha":
                    row["fecha"],

                "temporada":
                    row["temporada"],

                "hora":
                    instante.strftime(
                        "%H:%M"
                    )

            })

            instante += timedelta(
                minutes=30
            )

    cobertura = pd.DataFrame(
        registros
    )

    # =====================================
    # DIA SEMANA
    # =====================================

    cobertura["dia_semana"] = (

        cobertura["fecha"]

        .dt.day_name()

    )

    # =====================================
    # COBERTURA DIARIA
    # =====================================

    cobertura_dia = (

        cobertura

        .groupby(
            [
                "temporada",
                "fecha",
                "dia_semana",
                "hora"
            ]
        )

        .size()

        .reset_index(
            name="personas"
        )

    )

    # =====================================
    # DEMANDA MEDIA
    # =====================================

    demanda = (

        cobertura_dia

        .groupby(
            [
                "temporada",
                "dia_semana",
                "hora"
            ]
        )["personas"]

        .mean()

        .reset_index()

    )

    # =====================================
    # REDONDEO
    # =====================================

    demanda["demanda"] = (

        demanda["personas"]

        .round()

        .astype(int)

    )

    # =====================================
    # LIMPIEZA
    # =====================================

    demanda = demanda[
        [
            "dia_semana",
            "hora",
            "demanda"
        ]
    ]

    # =====================================
    # ORDENAR DIAS
    # =====================================

    orden = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    demanda["dia_semana"] = pd.Categorical(
        demanda["dia_semana"],
        categories=orden,
        ordered=True
    )

    demanda = demanda.sort_values(
        [
            "dia_semana",
            "hora"
        ]
    )

    demanda = demanda.reset_index(
        drop=True
    )

    # =====================================
    # ELIMINAR DIAS CERRADOS
    # =====================================

    horario_base = pd.read_excel(
        "data/inputs/horario_base.xlsx"
    )

    temporadas = pd.read_excel(
        "data/inputs/temporada.xlsx"
    )

    id_temporada = int(
        temporadas.loc[
            temporadas["nombre"] == temporada,
            "id"
        ].iloc[0]
    )

    dias_abiertos = horario_base[
        (horario_base["id_temporada"] == id_temporada)
        &
        (horario_base["abierto"] == 1)
    ]["dia_semana"].tolist()

    mapa = {
        "lunes": "Monday",
        "martes": "Tuesday",
        "miercoles": "Wednesday",
        "jueves": "Thursday",
        "viernes": "Friday",
        "sabado": "Saturday",
        "domingo": "Sunday"
    }

    dias_abiertos = [
        mapa[d]
        for d in dias_abiertos
    ]

    demanda = demanda[
        demanda["dia_semana"].isin(
            dias_abiertos
        )
    ].copy()

    return demanda