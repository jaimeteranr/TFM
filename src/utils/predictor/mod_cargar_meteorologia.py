"""
Módulo encargado de cargar y procesar la información meteorológica.

Obtiene los datos meteorológicos horarios y genera un conjunto de variables
agregadas a nivel diario que describen las condiciones ambientales durante
el horario de actividad del establecimiento. Los datos resultantes se
utilizan como variables de entrada en los modelos de predicción.
"""

import pandas as pd


class MeteorologiaLoader:
    """
    Gestiona la carga y transformación de la información meteorológica.

    Procesa los registros meteorológicos horarios y genera tanto la
    información original como un conjunto de indicadores diarios derivados,
    preparados para su integración con el resto de los datos del sistema.
    """

    def __init__(
        self,
        fichero="data/inputs/meteorologia.xlsx"
    ):

        self.fichero = fichero

    def cargar(self):

        df = pd.read_excel(
            self.fichero
        )

        # =====================================
        # FECHA
        # =====================================

        df["Fecha"] = pd.to_datetime(
            df["fecha_hora"]
        ).dt.normalize()

        df["hora"] = pd.to_datetime(
            df["fecha_hora"]
        ).dt.hour

        df["Hora"] = (
            df["fecha_hora"]
            .dt.strftime("%H:%M")
        )

        # =====================================
        # HORARIO NEGOCIO
        # =====================================

        negocio = df[
            (df["hora"] >= 12)
            |
            (df["hora"] <= 2)
        ].copy()

        # =====================================
        # VARIABLES DIARIAS
        # =====================================

        meteorologia_diaria = negocio.groupby(
            "Fecha"
        ).agg({

            "temperatura_celsius": [
                "mean",
                "max",
                "min"
            ],

            "humedad_porcentaje": "mean",

            "lluvia_mm": "sum",

            "nubosidad_porcentaje": "mean",

            "viento_km_h": "mean"

        })

        meteorologia_diaria.columns = [

            "temp_media",
            "temp_max",
            "temp_min",
            "humedad_media",
            "lluvia_total",
            "nubosidad_media",
            "viento_medio"

        ]

        # =====================================
        # VARIABLES EXTRA
        # =====================================

        meteorologia_diaria["amplitud_termica"] = (

            meteorologia_diaria["temp_max"]

            -

            meteorologia_diaria["temp_min"]

        )

        horas_lluvia = (

            negocio["lluvia_mm"] > 0

        ).groupby(

            negocio["Fecha"]

        ).sum()

        meteorologia_diaria["horas_lluvia"] = horas_lluvia

        horas_despejado = (

            negocio["weather_code"] == 0

        ).groupby(

            negocio["Fecha"]

        ).sum()

        meteorologia_diaria["horas_despejado"] = horas_despejado

        horas_nublado = (

            negocio["nubosidad_porcentaje"] >= 80

        ).groupby(

            negocio["Fecha"]

        ).sum()

        meteorologia_diaria["horas_muy_nublado"] = horas_nublado

        # =====================================
        # TEMPERATURA APERTURA
        # =====================================

        apertura = negocio[
            negocio["hora"] == 12
        ][[
            "Fecha",
            "temperatura_celsius"
        ]]

        apertura = apertura.rename(
            columns={
                "temperatura_celsius":
                "temp_apertura"
            }
        )

        meteorologia_diaria = meteorologia_diaria.merge(

            apertura,

            on="Fecha",

            how="left"

        )

        # =====================================
        # TEMPERATURA CIERRE
        # =====================================

        cierre = negocio[
            negocio["hora"] == 1
        ][[
            "Fecha",
            "temperatura_celsius"
        ]]

        cierre = cierre.rename(
            columns={
                "temperatura_celsius":
                "temp_cierre"
            }
        )

        meteorologia_diaria = meteorologia_diaria.merge(

            cierre,

            on="Fecha",

            how="left"

        )

        # =====================================
        # WEATHER CODE DOMINANTE
        # =====================================

        weather = (

            negocio

            .groupby("Fecha")["weather_code"]

            .agg(
                lambda x: x.mode().iloc[0]
            )

        )

        meteorologia_diaria["weather_code"] = weather.values

        # =====================================
        # LLOVIÓ
        # =====================================

        meteorologia_diaria["llovio"] = (

            meteorologia_diaria["lluvia_total"] > 0

        ).astype(int)

        meteorologia_diaria = meteorologia_diaria.reset_index()

        print(df.head())

        print()

        print(df.info())

        return df, meteorologia_diaria