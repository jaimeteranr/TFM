import pandas as pd


def obtener_temporada(fecha):

    fecha = pd.to_datetime(fecha)

    df = pd.read_excel(
        "data/inputs/temporada.xlsx"
    )

    fecha_md = (
        fecha.month,
        fecha.day
    )

    for _, fila in df.iterrows():

        inicio = pd.to_datetime(
            fila["fecha_inicio"]
        )

        fin = pd.to_datetime(
            fila["fecha_fin"]
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

    raise ValueError(
        "No se encontró temporada"
    )