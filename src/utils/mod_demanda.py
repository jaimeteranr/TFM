import pandas as pd
from datetime import timedelta


class DemandaExtractor:

    def __init__(self):

        self.horarios = None
        self.temporadas = None

    # =====================================
    # ASIGNAR TEMPORADA
    # =====================================

    def asignar_temporada(
        self,
        fecha
    ):

        fecha_md = (
            fecha.month,
            fecha.day
        )

        for _, fila in self.temporadas.iterrows():

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

            if inicio_md <= fin_md:

                if inicio_md <= fecha_md <= fin_md:

                    return fila["nombre"]

            else:

                if (
                    fecha_md >= inicio_md
                    or
                    fecha_md <= fin_md
                ):

                    return fila["nombre"]

        return None

    # =====================================
    # EXTRAER DEMANDA
    # =====================================

    def extraer(
        self,
        temporada
    ):

        # =====================================
        # CARGA
        # =====================================

        self.horarios = pd.read_excel(
            "data/inputs/horarios.xlsx"
        )

        self.temporadas = pd.read_excel(
            "data/inputs/temporada.xlsx"
        )

        # =====================================
        # FECHAS
        # =====================================

        self.horarios["fecha"] = pd.to_datetime(
            self.horarios["fecha"]
        )

        self.horarios["temporada"] = (

            self.horarios["fecha"]

            .apply(
                self.asignar_temporada
            )

        )

        self.horarios = self.horarios[

            self.horarios["temporada"]

            == temporada

        ].copy()

        # =====================================
        # NORMALIZAR TURNOS
        # =====================================

        self.horarios["entrada_norm"] = (

            pd.to_datetime(

                "1900-01-01 "

                +

                self.horarios["entrada"].astype(str)

            )

            .dt.round("30min")

        )

        self.horarios["duracion_norm"] = (

            (

                self.horarios["duracion_turno"]

                * 2

            )

            .round()

            / 2

        )

        # =====================================
        # EXPANDIR TURNOS
        # =====================================

        registros = []

        for _, row in self.horarios.iterrows():

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
                        instante.strftime("%H:%M")

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

        demanda = demanda[

            [

                "dia_semana",

                "hora",

                "demanda"

            ]

        ]

        # =====================================
        # ORDENAR
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
        # ELIMINAR DÍAS CERRADOS
        # =====================================

        horario_base = pd.read_excel(
            "data/inputs/horario_base.xlsx"
        )

        id_temporada = int(

            self.temporadas.loc[

                self.temporadas["nombre"] == temporada,

                "id"

            ].iloc[0]

        )

        dias_abiertos = horario_base[

            (

                horario_base["id_temporada"]

                == id_temporada

            )

            &

            (

                horario_base["abierto"]

                == 1

            )

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

            demanda["dia_semana"]

            .isin(dias_abiertos)

        ].copy()

        return demanda