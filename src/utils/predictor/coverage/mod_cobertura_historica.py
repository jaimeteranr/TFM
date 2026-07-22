"""
Módulo encargado de construir la cobertura histórica de personal a partir
de los horarios reales de los trabajadores.

Procesa los turnos almacenados en el histórico, los normaliza y calcula el
número de empleados presentes en cada intervalo de 30 minutos. Además,
permite filtrar la información por temporada para generar coberturas
históricas específicas que posteriormente pueden utilizarse para el
entrenamiento y evaluación de los modelos de predicción.
"""

import pandas as pd
from datetime import timedelta

class CoberturaHistorica:
    """
    Construye la cobertura histórica de personal a partir de los horarios
    registrados.

    A partir de los turnos reales de los trabajadores, genera una serie
    temporal con el número de personas presentes en cada intervalo horario,
    pudiendo limitar el cálculo a una temporada concreta.
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
    
    def construir(
        self,
        temporada=None
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

        if temporada is not None:
            self.horarios = self.horarios[
                self.horarios["temporada"] == temporada
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

                fecha_real = row["fecha"] + pd.Timedelta(
                    days=(instante.day - inicio.day)
                )

                datetime_real = pd.Timestamp(
                    year=fecha_real.year,
                    month=fecha_real.month,
                    day=fecha_real.day,
                    hour=instante.hour,
                    minute=instante.minute
                )

                registros.append({

                    "datetime": datetime_real,
                    "temporada": row["temporada"]

                })

                instante += timedelta(minutes=30)

        cobertura = pd.DataFrame(registros)

        if cobertura.empty:
            return cobertura

        cobertura = (
            cobertura
            .groupby(["datetime", "temporada"])
            .size()
            .reset_index(name="personas")
            .sort_values("datetime")
            .reset_index(drop=True)
        )

        return cobertura
