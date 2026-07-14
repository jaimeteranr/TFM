import pandas as pd


class Temporada:

    def obtener_temporada(
        self,
        fecha
    ):

        fecha = pd.to_datetime(fecha)

        temporadas = pd.read_excel(
            "data/inputs/temporada.xlsx"
        )

        fecha_md = (
            fecha.month,
            fecha.day
        )

        for _, fila in temporadas.iterrows():

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

            # ==========================
            # TEMPORADA NORMAL
            # ==========================

            if inicio_md <= fin_md:

                if (
                    inicio_md
                    <= fecha_md
                    <= fin_md
                ):

                    return fila["nombre"]

            # ==========================
            # TEMPORADA QUE CRUZA AÑO
            # ==========================

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