"""
Módulo encargado de obtener la información meteorológica necesaria para los
modelos de predicción.

Proporciona una interfaz unificada para acceder tanto a datos históricos
como a predicciones meteorológicas, seleccionando automáticamente la fuente
de información más adecuada en función del periodo solicitado y devolviendo
los datos en un formato homogéneo.
"""

import requests
import pandas as pd


class OpenMeteoLoader:
    """
    Gestiona la obtención de la información meteorológica.

    Recupera los datos meteorológicos correspondientes al intervalo temporal
    solicitado, utilizando información histórica o previsiones futuras según
    corresponda, y los prepara para su integración con el resto de los datos
    del sistema.
    """

    def __init__(

        self,

        latitud=43.4623,

        longitud=-3.8099

    ):

        # Santander

        self.latitud = latitud

        self.longitud = longitud

    def obtener(
        self,
        fecha_inicio,
        fecha_fin
    ):

        from datetime import date
        import pandas as pd

        fecha = pd.to_datetime(fecha_inicio).date()

        if fecha < date.today():

            return self.obtener_historico(
                fecha_inicio,
                fecha_fin
            )

        return self.obtener_prediccion(
            fecha_inicio,
            fecha_fin
        )

    def obtener_historico(
        self,
        fecha_inicio,
        fecha_fin
    ):

        import pandas as pd

        meteorologia = pd.read_excel(
            "data/inputs/meteorologia.xlsx"
        )

        meteorologia["fecha_hora"] = pd.to_datetime(
            meteorologia["fecha_hora"]
        )

        fecha_inicio = pd.to_datetime(fecha_inicio)
        fecha_fin = pd.to_datetime(fecha_fin) + pd.Timedelta(days=1)

        meteorologia = meteorologia[
            (meteorologia["fecha_hora"] >= fecha_inicio)
            &
            (meteorologia["fecha_hora"] < fecha_fin)
        ].copy()

        # Crear las mismas columnas que usa FutureDatasetBuilder
        meteorologia["Fecha"] = meteorologia["fecha_hora"].dt.normalize()
        meteorologia["Hora"] = meteorologia["fecha_hora"].dt.strftime("%H:%M")

        return meteorologia

    # =====================================
    # DESCARGAR PREVISIÓN
    # =====================================

    def obtener_prediccion(

        self,

        fecha_inicio,

        fecha_fin

    ):

        url = (

            "https://api.open-meteo.com/v1/forecast"

        )

        parametros = {

            "latitude": self.latitud,

            "longitude": self.longitud,

            "start_date": fecha_inicio,

            "end_date": fecha_fin,

            "hourly": ",".join([

                "temperature_2m",

                "relative_humidity_2m",

                "precipitation",

                "cloud_cover",

                "wind_speed_10m",

                "weather_code"

            ]),

            "timezone": "Europe/Madrid"

        }

        respuesta = requests.get(

            url,

            params=parametros,

            timeout=30

        )

        respuesta.raise_for_status()

        datos = respuesta.json()

        hourly = datos["hourly"]

        dataset = pd.DataFrame({

            "datetime":

                pd.to_datetime(

                    hourly["time"]

                ),

            "temperatura_celsius":

                hourly["temperature_2m"],

            "humedad_porcentaje":

                hourly["relative_humidity_2m"],

            "lluvia_mm":

                hourly["precipitation"],

            "nubosidad_porcentaje":

                hourly["cloud_cover"],

            "viento_km_h":

                hourly["wind_speed_10m"],

            "weather_code":

                hourly["weather_code"]

        })

        dataset["Fecha"] = dataset["datetime"].dt.normalize()

        dataset["hora"] = dataset["datetime"].dt.hour

        dataset["Hora"] = (

            dataset["hora"]

            .astype(str)

            .str.zfill(2)

            + ":00"

        )

        return dataset