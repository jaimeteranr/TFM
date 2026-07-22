"""
Módulo que define la estructura base para los modelos de predicción de
cobertura.

Proporciona la funcionalidad común para la preparación del dataset, la
separación de los datos de entrenamiento y prueba, la generación de
predicciones y la evaluación de resultados. Los modelos específicos heredan
de esta clase e implementan únicamente el algoritmo de aprendizaje.
"""

import pandas as pd

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


class ModelBaseCobertura:
    """
    Clase base para los modelos de predicción de cobertura.

    Centraliza las operaciones comunes del proceso de entrenamiento y
    evaluación de modelos de Machine Learning, incluyendo la preparación de
    los datos, la gestión de los conjuntos de entrenamiento y prueba, la
    evaluación del rendimiento y el análisis de las predicciones.

    Las clases derivadas son responsables de implementar el método de
    entrenamiento del modelo concreto.
    """

    def __init__(
        self,
        dataset
    ):

        self.dataset = dataset.copy()

        # =====================================
        # COLUMNAS AUXILIARES
        # =====================================

        self.dataset["Fecha"] = (
            self.dataset["datetime"]
            .dt.normalize()
        )

        self.dataset["Hora"] = (
            self.dataset["datetime"]
            .dt.strftime("%H:%M")
        )

        self.dataset["hora_racing_decimal"] = (
            self.dataset["hora_racing_decimal"]
            .fillna(0)
        )

        self.model = None

        self.X_train = None
        self.X_test = None

        self.y_train = None
        self.y_test = None

        self.predicciones = None

        self.test = None

    FEATURES = [
        "ventas",
        "temperatura_celsius",
        "humedad_porcentaje",
        "lluvia_mm",
        "nubosidad_porcentaje",
        "viento_km_h",
        "weather_code",
        "hora",
        "minuto",
        "dia_semana",
        "mes",
        "dia_mes",
        "fin_semana",
        "temporada",
        "festivo",
        "prefestivo",
        "evento",
        "evento_importancia",
        "racing",
        "hora_racing_decimal",
        "racing_tarde",
        "racing_noche"
    ]

    TARGET = "personas"

    # =====================================
    # PREPARAR DATASET
    # =====================================

    def preparar_dataset(self):

        X = self.dataset[
            self.FEATURES
        ]

        y = self.dataset[
            self.TARGET
        ]

        return X, y

    # =====================================
    # TRAIN / TEST
    # =====================================

    def separar_train_test(
        self,
        dia_referencia=15
    ):

        dataset = self.dataset.copy()

        # =====================================
        # MARCAR FILAS DE TEST
        # =====================================

        dataset["test"] = False

        # =====================================
        # UNA SEMANA POR CADA MES
        # =====================================

        meses = (

            dataset[["Fecha"]]

            .assign(

                año=lambda x: x["Fecha"].dt.year,

                mes=lambda x: x["Fecha"].dt.month

            )

            .drop_duplicates(
                ["año", "mes"]
            )

        )

        for _, fila in meses.iterrows():

            año = fila["año"]

            mes = fila["mes"]

            fecha_ref = pd.Timestamp(

                year=año,

                month=mes,

                day=dia_referencia

            )

            lunes = (

                fecha_ref

                -

                pd.Timedelta(
                    days=fecha_ref.weekday()
                )

            )

            domingo = (

                lunes

                +

                pd.Timedelta(days=6)

            )

            dataset.loc[

                (dataset["Fecha"] >= lunes)

                &

                (dataset["Fecha"] <= domingo),

                "test"

            ] = True

        # =====================================
        # TRAIN / TEST
        # =====================================

        train = dataset[
            ~dataset["test"]
        ].copy()

        test = dataset[
            dataset["test"]
        ].copy()

        self.test = test.copy()

        self.X_train = train[
            self.FEATURES
        ]

        self.y_train = train[
            self.TARGET
        ]

        self.X_test = test[
            self.FEATURES
        ]

        self.y_test = test[
            self.TARGET
        ]

        # =====================================
        # INFORMACIÓN
        # =====================================

        print("\n========================")
        print("TRAIN / TEST")
        print("========================\n")

        print(
            "Train:",
            len(train)
        )

        print(
            "Test:",
            len(test)
        )

        print()

        print(
            "Train:",
            train["Fecha"].min().date(),
            "->",
            train["Fecha"].max().date()
        )

        print(
            "Test:",
            test["Fecha"].min().date(),
            "->",
            test["Fecha"].max().date()
        )

        print()

        print("Semanas utilizadas como TEST:\n")

        semanas = (

            test[["Fecha"]]

            .drop_duplicates()

            .assign(

                año=lambda x: x["Fecha"].dt.year,

                mes=lambda x: x["Fecha"].dt.month,

                semana=lambda x: x["Fecha"].dt.isocalendar().week

            )

            .groupby(
                ["año", "mes"]
            )["semana"]

            .first()

        )

        for (año, mes), semana in semanas.items():

            print(
                f"{año}-{mes:02d} -> Semana {semana}"
            )

    def asignar_train_test(

        self,

        X_train,
        y_train,

        X_test,
        y_test

    ):

        self.X_train = X_train
        self.y_train = y_train

        self.X_test = X_test
        self.y_test = y_test

    # =====================================
    # ENTRENAR
    # =====================================

    def entrenar(self):

        raise NotImplementedError(
            "Cada modelo debe implementar entrenar()"
        )

    # =====================================
    # PREDECIR
    # =====================================

    def predecir(self):

        self.predicciones = self.model.predict(
            self.X_test
        )

    # =====================================
    # EVALUAR
    # =====================================

    def evaluar(self):

        mae = mean_absolute_error(

            self.y_test,

            self.predicciones

        )

        mse = mean_squared_error(

            self.y_test,

            self.predicciones

        )

        rmse = mse ** 0.5

        r2 = r2_score(

            self.y_test,

            self.predicciones

        )

        print("\n========================")
        print("RESULTADOS")
        print("========================\n")

        print(f"MAE : {mae:.2f}")

        print(f"RMSE: {rmse:.2f}")

        print(f"R²  : {r2:.4f}")

    # =====================================
    # IMPORTANCIA VARIABLES
    # =====================================

    def importancia_variables(self):

        if not hasattr(

            self.model,

            "feature_importances_"

        ):

            print(
                "El modelo no dispone de importancia de variables."
            )

            return

        importancia = pd.DataFrame({

            "Variable": self.FEATURES,

            "Importancia": self.model.feature_importances_

        })

        importancia = importancia.sort_values(

            "Importancia",

            ascending=False

        )

        print("\n========================")
        print("IMPORTANCIA VARIABLES")
        print("========================\n")

        print(importancia)

    # =====================================
    # MOSTRAR PREDICCIONES
    # =====================================

    def mostrar_predicciones(
        self,
        n=20
    ):

        resultados = pd.DataFrame({

            "Fecha": self.test["Fecha"].values,

            "Hora": self.test["Hora"].values,

            "Ventas": self.test["ventas"].values,

            "Personas reales": self.y_test.values,

            "Predicción": self.predicciones

        })

        resultados["Error"] = (

            resultados["Predicción"]

            -

            resultados["Personas reales"]

        )

        print("\n========================")
        print("PREDICCIONES")
        print("========================\n")

        print(
            resultados.head(n)
        )

        print()

        print(
            "Error medio:",
            resultados["Error"].abs().mean()
        )

        print("\n========================")
        print("MAYORES ERRORES")
        print("========================\n")

        print(

            resultados.reindex(

                resultados["Error"]

                .abs()

                .sort_values(

                    ascending=False

                ).index

            ).head(20)

        )