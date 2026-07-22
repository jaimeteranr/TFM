"""
Módulo encargado de construir el conjunto de datos utilizado para el
entrenamiento del modelo de predicción de cobertura.

Integra la cobertura histórica de personal con las ventas, la información
meteorológica, los eventos y las variables temporales, generando un dataset
completo con las variables explicativas y la demanda real de trabajadores
para cada intervalo horario.
"""

import pandas as pd
from mod_cargar_ventas_horario import VentasLoader
from datetime import timedelta
from src.utils.predictor.coverage.mod_cobertura_historica import CoberturaHistorica
from mod_cargar_meteorologia import MeteorologiaLoader
from mod_cargar_eventos import EventosLoader

class DatasetCoberturaBuilder:
    """
    Construye el dataset de entrenamiento del modelo de cobertura.

    Coordina la carga, integración y transformación de las distintas fuentes
    de información necesarias para generar un conjunto de datos preparado
    para el entrenamiento del modelo de Machine Learning encargado de
    predecir la demanda de personal.
    """

    def __init__(self):

        self.meteorologia, _ = MeteorologiaLoader().cargar()

        self.eventos = EventosLoader().cargar()

    def cargar_datos(self):

        self.horarios = pd.read_excel(
            "data/inputs/horarios.xlsx"
        )

        self.ventas = VentasLoader().cargar()

    # def construir_cobertura(self):

    #     registros = []

    #     for _, fila in self.horarios.iterrows():

    #         fecha = pd.to_datetime(
    #             fila["fecha"]
    #         )

    #         entrada = fila["entrada"]

    #         duracion = float(
    #             fila["duracion_turno"]
    #         )

    #         instante = pd.Timestamp(
    #             year=fecha.year,
    #             month=fecha.month,
    #             day=fecha.day,
    #             hour=entrada.hour,
    #             minute=entrada.minute
    #         )

    #         for _ in range(int(duracion)):

    #             registros.append({

    #                 "datetime": instante

    #             })

    #             instante += timedelta(
    #                 hours=1
    #             )

    #     cobertura = pd.DataFrame(
    #         registros
    #     )

    #     cobertura = (

    #         cobertura

    #         .groupby("datetime")

    #         .size()

    #         .reset_index(
    #             name="personas"
    #         )

    #     )

    #     self.cobertura = cobertura

    #     return cobertura

    def expandir_ventas_30min(self):

        ventas = self.ventas.copy()

        registros = []

        for _, fila in ventas.iterrows():

            registros.append({
                "datetime": fila["datetime"],
                "ventas": fila["ventas"] / 2
            })

            registros.append({
                "datetime": fila["datetime"] + pd.Timedelta(minutes=30),
                "ventas": fila["ventas"] / 2
            })

        return (
            pd.DataFrame(registros)
            .sort_values("datetime")
            .reset_index(drop=True)
        )
    
    def unir_datos(
        self,
        ventas,
        cobertura
    ):

        dataset = cobertura.merge(
            ventas,
            on="datetime",
            how="inner"
        )

        dataset = (
            dataset
            .sort_values("datetime")
            .reset_index(drop=True)
        )

        return dataset
    
    def expandir_meteorologia_30min(self):

        meteo = self.meteorologia.copy()

        registros = []

        for _, fila in meteo.iterrows():

            # Registro de la hora en punto
            registros.append(fila.to_dict())

            # Registro de la media hora
            fila_media = fila.copy()

            fila_media["fecha_hora"] = (
                fila["fecha_hora"] + pd.Timedelta(minutes=30)
            )

            fila_media["Hora"] = fila_media["fecha_hora"].strftime("%H:%M")

            registros.append(fila_media.to_dict())

        return (
            pd.DataFrame(registros)
            .sort_values("fecha_hora")
            .reset_index(drop=True)
        )
    
        
    def enriquecer_dataset(self, dataset):

        dataset = dataset.copy()

        dataset["Fecha"] = dataset["datetime"].dt.normalize()

        dataset["Hora"] = dataset["datetime"].dt.strftime("%H:%M")

        self.meteorologia = self.expandir_meteorologia_30min()

        # Meteorología
        dataset = dataset.merge(
            self.meteorologia,
            on=["Fecha", "Hora"],
            how="left"
        )

        # Eventos
        dataset = dataset.merge(
            self.eventos,
            on="Fecha",
            how="left"
        )

        # Eliminar columnas auxiliares
        dataset = dataset.drop(
            columns=["Fecha", "Hora", "fecha_hora"]
        )

        return dataset
    
    def generar_variables(
        self,
        dataset
    ):

        dataset = dataset.copy()

        dataset["hora"] = dataset["datetime"].dt.hour

        dataset["minuto"] = dataset["datetime"].dt.minute

        dataset["dia_semana"] = dataset["datetime"].dt.dayofweek

        dataset["mes"] = dataset["datetime"].dt.month

        dataset["dia_mes"] = dataset["datetime"].dt.day

        dataset["fin_semana"] = (
            dataset["dia_semana"]
            .isin([5, 6])
            .astype(int)
        )

        dataset["temporada"] = (
        dataset["temporada"]
        .map({
            "invierno": 0,
            "verano": 1
        })
        .astype(int)
    )

        return dataset

    def construir(self):

        self.cargar_datos()

        ventas = self.expandir_ventas_30min()

        cobertura = CoberturaHistorica().construir()

        dataset = self.unir_datos(
            ventas,
            cobertura
        )

        dataset = self.enriquecer_dataset(
            dataset
        )

        dataset = self.generar_variables(
            dataset
        )

        return dataset