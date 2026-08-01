"""
Módulo encargado de obtener la demanda de personal utilizada por el
planificador.

Genera la demanda requerida para cada intervalo horario a partir de la
cobertura histórica o de las predicciones de ventas y cobertura futura,
proporcionando un formato unificado que sirve como entrada para los procesos
de planificación de calendarios.
"""

import pandas as pd
from datetime import timedelta
from src.utils.predictor.coverage.mod_cobertura_historica import CoberturaHistorica
from variables_entrada import (MODO_DEBUG)

from src.utils.predictor.mod_cargar_ventas_horario import VentasLoader
from src.utils.predictor.mod_cargar_eventos import EventosLoader
from src.utils.predictor.forecast.mod_calendar_predictor import CalendarPredictor
from src.utils.predictor.coverage.mod_coverage_predictor import CoveragePredictor


class DemandaExtractor:
    """
    Gestiona la obtención de la demanda de personal para el planificador.

    Extrae la demanda tanto a partir del histórico de cobertura como de las
    predicciones generadas por los modelos del sistema, transformando la
    información obtenida en un conjunto de datos homogéneo preparado para su
    utilización en la generación de calendarios de trabajo.
    """

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

    def extraer_historica(
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

        # # =====================================
        # # NORMALIZAR TURNOS
        # # =====================================

        # self.horarios["entrada_norm"] = (

        #     pd.to_datetime(

        #         "1900-01-01 "

        #         +

        #         self.horarios["entrada"].astype(str)

        #     )

        #     .dt.round("30min")

        # )

        # self.horarios["duracion_norm"] = (

        #     (

        #         self.horarios["duracion_turno"]

        #         * 2

        #     )

        #     .round()

        #     / 2

        # )

        # # =====================================
        # # EXPANDIR TURNOS
        # # =====================================

        # registros = []

        # for _, row in self.horarios.iterrows():

        #     inicio = row["entrada_norm"]

        #     fin = inicio + pd.Timedelta(

        #         hours=row["duracion_norm"]

        #     )

        #     instante = inicio

        #     while instante < fin:

        #         registros.append({

        #             "fecha":
        #                 row["fecha"],

        #             "temporada":
        #                 row["temporada"],

        #             "hora":
        #                 instante.strftime("%H:%M")

        #         })

        #         instante += timedelta(
        #             minutes=30
        #         )

        # cobertura = pd.DataFrame(
        #     registros
        # )

        cobertura = CoberturaHistorica().construir(
            temporada=temporada
        )

        cobertura["fecha"] = cobertura["datetime"].dt.normalize()

        cobertura["hora"] = cobertura["datetime"].dt.strftime("%H:%M")

        cobertura["dia_semana"] = cobertura["datetime"].dt.day_name()

        # # =====================================
        # # DIA SEMANA
        # # =====================================

        # cobertura["dia_semana"] = (

        #     cobertura["fecha"]

        #     .dt.day_name()

        # )

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
    
    def extraer_prediccion(
        self,
        fecha_inicio
    ):

        # =====================================
        # FECHAS
        # =====================================

        fecha_inicio = pd.to_datetime(fecha_inicio)

        fecha_fin = fecha_inicio + timedelta(days=6)

        # =====================================
        # CARGAR DATOS
        # =====================================

        historico = VentasLoader().cargar()

        eventos = EventosLoader().cargar()

        # =====================================
        # PREDECIR VENTAS
        # =====================================

        predictor = CalendarPredictor()

        prediccion = predictor.predecir(

            historico=historico,

            fecha_inicio=fecha_inicio,

            fecha_fin=fecha_fin,

            eventos=eventos

        )

        if MODO_DEBUG:
            print("\n========================")
            print("VENTAS PREDICHAS")
            print("========================\n")

            print(
                prediccion[
                    [
                        "datetime",
                        "ventas"
                    ]
                ]
            )

            print("\nTotal registros:", len(prediccion))

        # =====================================
        # PREDECIR COBERTURA
        # =====================================

        prediccion = CoveragePredictor().predecir(
            prediccion
        )

        if MODO_DEBUG:
            print("\n========================")
            print("VENTAS + DEMANDA")
            print("========================\n")

            print(
                prediccion[
                    [
                        "datetime",
                        "ventas",
                        "personas"
                    ]
                ]
            )

            print("\nTotal registros:", len(prediccion))

        # =====================================
        # FORMATO DEMANDA
        # =====================================

        prediccion["dia_semana"] = (
            prediccion["datetime"]
            .dt.day_name()
        )

        demanda = prediccion[
            [
                "dia_semana",
                "Hora",
                "personas"
            ]
        ].copy()

        demanda = demanda.rename(
            columns={
                "Hora": "hora",
                "personas": "demanda"
            }
        )

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
        ).reset_index(drop=True)

        return demanda