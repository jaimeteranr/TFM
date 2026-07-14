import pandas as pd


class DatasetBuilder:

    def __init__(
        self,
        ventas,
        meteorologia,
        eventos
    ):

        self.ventas = ventas
        self.meteorologia = meteorologia
        self.eventos = eventos

    def crear(self):

        # ==========================
        # UNIÓN VENTAS + METEOROLOGÍA
        # ==========================

        dataset = self.ventas.merge(

            self.meteorologia,

            on="Fecha",

            how="inner"

        )

        # ==========================
        # UNIÓN CON EVENTOS
        # ==========================

        dataset = dataset.merge(

            self.eventos,

            on="Fecha",

            how="left"

        )

        # =====================================
        # VARIABLES TEMPORALES
        # =====================================

        dataset["año"] = dataset["Fecha"].dt.year

        dataset["mes"] = dataset["Fecha"].dt.month

        dataset["dia_mes"] = dataset["Fecha"].dt.day

        dataset["semana"] = (
            dataset["Fecha"]
            .dt
            .isocalendar()
            .week
            .astype(int)
        )

        dataset["trimestre"] = dataset["Fecha"].dt.quarter

        dataset["dia_año"] = dataset["Fecha"].dt.dayofyear

        dataset["dia_semana_nombre"] = dataset["Fecha"].dt.day_name()

        # =====================================
        # VARIABLES HISTÓRICAS DE VENTAS
        # =====================================

        dataset = dataset.sort_values("Fecha")

        dataset["beneficio_lag_1"] = dataset["Beneficio"].shift(1)

        dataset["beneficio_lag_7"] = dataset["Beneficio"].shift(7)

        dataset["beneficio_lag_14"] = dataset["Beneficio"].shift(14)

        dataset["cantidad_lag_1"] = dataset["Cantidad"].shift(1)

        dataset["cantidad_lag_7"] = dataset["Cantidad"].shift(7)

        dataset["cantidad_lag_14"] = dataset["Cantidad"].shift(14)

        dataset["beneficio_media_7d"] = (

            dataset["Beneficio"]

            .rolling(7)

            .mean()

            .shift(1)

        )

        dataset["cantidad_media_7d"] = (

            dataset["Cantidad"]

            .rolling(7)

            .mean()

            .shift(1)

        )

        # ==========================
        # ELIMINAR DÍAS CERRADOS
        # ==========================

        dataset = dataset[

            (dataset["Beneficio"] > 50)

            &

            (dataset["Cantidad"] > 0)

        ].copy()

        # ==========================
        # LIMPIEZA
        # ==========================

        dataset = dataset.reset_index(
            drop=True
        )

        dataset = dataset.drop(
            columns=[
                "index",
                "horario_racing",
                "evento_nombre"
            ],
            errors="ignore"
        )

        return dataset