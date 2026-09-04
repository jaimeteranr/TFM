"""
Módulo que define la estructura base para los modelos de predicción de
ventas.

Proporciona la funcionalidad común para la preparación del dataset, la
separación de los datos de entrenamiento y prueba, la generación de
predicciones y la evaluación de resultados. Los modelos específicos heredan
de esta clase e implementan únicamente el algoritmo de aprendizaje.
"""

import pandas as pd
import numpy as np
import time

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from variables_entrada import TIPO_SPLIT

class ModelBase:
    """
    Clase base para los modelos de predicción de ventas.

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

        self.dataset = dataset

        self.model = None

        # =====================================
        # PREPROCESADO
        # =====================================

        self.importancias = None
        self.scaler_X = None
        self.scaler_y = None

        self.X_train = None
        self.X_test = None

        self.y_train = None
        self.y_test = None

        self.predicciones = None
        self.test = None
        self.train = None

        # =====================================
        # TIEMPOS
        # =====================================

        self.training_time = None
        self.prediction_time = None

    FEATURES = [

        "temperatura_celsius",
        "humedad_porcentaje",
        "lluvia_mm",
        "nubosidad_porcentaje",
        "viento_km_h",
        "weather_code",
        "hora",
        "dia_semana",
        "festivo",
        "prefestivo",
        "fin_semana",
        "evento",
        "evento_importancia",
        "racing",
        "hora_racing_decimal",
        "racing_tarde",
        "racing_noche",
        "hora_fin_semana",
        "ventas_lag_1h",
        "ventas_lag_2h",
        "ventas_lag_24h",
        "ventas_lag_168h",
        "ventas_media_3h",
        "ventas_media_24h"

    ]

    TARGET = "ventas"

    def preparar_dataset(self):

        X = self.dataset[
            self.FEATURES
        ]

        y = self.dataset[
            self.TARGET
        ]

        return X, y

    def separar_temporadas(self):

        dataset = self.dataset.copy()

        fecha = dataset["Fecha"]

        # =====================================
        # VERANO
        # 15 JUNIO -> 15 SEPTIEMBRE
        # =====================================

        verano = dataset[
            (
                (
                    (fecha.dt.month == 6)
                    & (fecha.dt.day >= 15)
                )
                |
                (fecha.dt.month.isin([7, 8]))
                |
                (
                    (fecha.dt.month == 9)
                    & (fecha.dt.day <= 15)
                )
            )
        ].copy()

        # =====================================
        # INVIERNO
        # 16 SEPTIEMBRE -> 14 JUNIO
        # =====================================

        invierno = dataset[
            ~dataset.index.isin(
                verano.index
            )
        ].copy()

        return verano, invierno
    
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

            # -------------------------
            # Día de referencia
            # -------------------------

            fecha_ref = pd.Timestamp(
                year=año,
                month=mes,
                day=dia_referencia
            )

            # -------------------------
            # Lunes de esa semana
            # -------------------------

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

        self.train = train.copy()

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

    # =====================================
    # TRAIN / TEST TEMPORAL
    # =====================================

    def separar_train_test_temporal(
        self,
        porcentaje_train=0.75
    ):

        dataset = self.dataset.copy()

        # =====================================
        # ORDENAR POR FECHA
        # =====================================

        dataset = dataset.sort_values(
            "Fecha"
        ).copy()

        # =====================================
        # PUNTO DE CORTE
        # =====================================

        indice_corte = int(
            len(dataset) * porcentaje_train
        )

        # =====================================
        # TRAIN / TEST
        # =====================================

        train = dataset.iloc[
            :indice_corte
        ].copy()

        test = dataset.iloc[
            indice_corte:
        ].copy()

        # =====================================
        # GUARDAR
        # =====================================

        self.train = train.copy()

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

        print()
        print("========================")
        print("TRAIN / TEST TEMPORAL")
        print("========================")
        print()

        print(
            f"Train: {len(train)} "
            f"({len(train) / len(dataset) * 100:.1f}%)"
        )

        print(
            f"Test: {len(test)} "
            f"({len(test) / len(dataset) * 100:.1f}%)"
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

    def preparar_train_test(self):

        if TIPO_SPLIT == "mensual":

            self.separar_train_test()

        elif TIPO_SPLIT == "temporal":

            self.separar_train_test_temporal()

        else:

            raise ValueError(
                f"TIPO_SPLIT desconocido: {TIPO_SPLIT}"
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
    # MEDIR TIEMPO DE ENTRENAMIENTO
    # =====================================

    def medir_entrenamiento(self):

        print(
            f"\n>>> MIDIENDO ENTRENAMIENTO: {type(self).__name__}"
        )

        inicio = time.perf_counter()

        self.entrenar()

        self.training_time = (
            time.perf_counter() - inicio
        )

        print(
            f">>> TIEMPO: {self.training_time:.3f} s"
        )


    # =====================================
    # MEDIR TIEMPO DE PREDICCIÓN
    # =====================================

    def medir_prediccion(self):

        print(
            f"\n>>> MIDIENDO PREDICCIÓN: {type(self).__name__}"
        )

        inicio = time.perf_counter()

        self.predecir()

        self.prediction_time = (
            time.perf_counter() - inicio
        )

        print(
            f">>> TIEMPO: {self.prediction_time * 1000:.2f} ms"
        )

    # =====================================
    # ENTRENAR
    # =====================================

    def entrenar(self):

        raise NotImplementedError(
            "Cada modelo debe implementar entrenar()"
        )
    
    # =====================================
    # GUARDAR MODELO
    # =====================================

    def guardar_modelo(self):

        """
        Cada modelo implementará su propio sistema
        de almacenamiento.
        """

        pass

    # =====================================
    # CARGAR MODELO
    # =====================================

    def cargar_modelo(self):

        """
        Cada modelo implementará su propio sistema
        de carga.
        """

        pass
    
    # =====================================
    # PREDICCIÓN DEL MODELO
    # =====================================

    def predecir_modelo(self, X):

        """
        Método genérico de predicción.

        Los modelos que necesiten un preprocesado adicional
        (por ejemplo redes neuronales) pueden sobreescribir
        este método.
        """

        return self.model.predict(X)
    
    # =====================================
    # PREDECIR
    # =====================================

    def predecir(self):

        self.predicciones = self.predecir_modelo(
            self.X_test
        )

        # Algunos modelos (TensorFlow) devuelven un vector columna

        import numpy as np
        self.predicciones = np.asarray(self.predicciones).ravel()


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

        if self.training_time is not None:

            print(
                f"Tiempo entrenamiento: {self.training_time:.3f} s"
            )

        if self.prediction_time is not None:

            print(
                f"Tiempo predicción: {self.prediction_time*1000:.2f} ms"
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

        if hasattr(self.model, "feature_importances_"):

            importancia = pd.DataFrame({

                "Variable": self.FEATURES,

                "Importancia": self.model.feature_importances_

            })

        elif hasattr(self, "importancias"):

            importancia = self.importancias.copy()

        else:

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
        print("\n========================")
        print("DEBUG MOSTRAR PREDICCIONES")
        print("========================")

        print("len test:", len(self.test))
        print("len Fecha:", len(self.test["Fecha"]))
        print("len Hora:", len(self.test["Hora"]))
        print("len y_test:", len(np.asarray(self.y_test).ravel()))
        print("len predicciones:", len(np.asarray(self.predicciones).ravel()))

        # =====================================
        # ALINEAR TEST CON LAS PREDICCIONES
        # =====================================

        # =====================================
        # ALINEAR TEST, Y_TEST Y PREDICCIONES
        # =====================================

        y_test = np.asarray(
            self.y_test
        ).ravel()

        predicciones = np.asarray(
            self.predicciones
        ).ravel()

        test = self.test.copy()

        # -------------------------------------
        # COMPROBAR LONGITUDES
        # -------------------------------------

        print()
        print("LONGITUDES ANTES DE ALINEAR")
        print("----------------------------")
        print("test:", len(test))
        print("y_test:", len(y_test))
        print("predicciones:", len(predicciones))

        # -------------------------------------
        # LONGITUD COMÚN
        # -------------------------------------

        n = min(
            len(test),
            len(y_test),
            len(predicciones)
        )

        # -------------------------------------
        # QUEDARNOS CON LAS ÚLTIMAS N FILAS
        # -------------------------------------

        test = test.iloc[-n:].copy()

        y_test = y_test[-n:]

        predicciones = predicciones[-n:]

        # -------------------------------------
        # COMPROBACIÓN
        # -------------------------------------

        print()
        print("LONGITUDES DESPUÉS DE ALINEAR")
        print("-------------------------------")
        print("test:", len(test))
        print("y_test:", len(y_test))
        print("predicciones:", len(predicciones))

        # =====================================
        # CONSTRUIR RESULTADOS
        # =====================================

        resultados = pd.DataFrame({

            "Fecha": test["Fecha"].values,

            "Hora": test["Hora"].values,

            "Venta real": y_test,

            "Predicción": predicciones

        })

        resultados["Error"] = (

            resultados["Predicción"]

            -

            resultados["Venta real"]

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
