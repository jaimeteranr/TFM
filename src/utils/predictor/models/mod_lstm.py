"""
Módulo que implementa un modelo de predicción basado en redes neuronales LSTM.

La red aprende patrones temporales utilizando secuencias de observaciones
horarias consecutivas para estimar las ventas de la hora siguiente.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    LSTM,
    Dense,
    Dropout
)
from tensorflow.keras.callbacks import EarlyStopping

from .mod_model_base import ModelBase
from variables_entrada import TIPO_SPLIT


SEQUENCE_LENGTH = 24

FEATURES_LSTM = [
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

    "racing",
    "hora_racing_decimal",

    "ventas"

]

N_FEATURES = len(FEATURES_LSTM)


class LSTMModel(ModelBase):

    def __init__(
        self,
        dataset,
        ruta_modelo=None
    ):

        super().__init__(dataset)

        self.scaler_X = MinMaxScaler()

        self.scaler_y = MinMaxScaler()

        self.sequence_length = SEQUENCE_LENGTH

        self.ruta_modelo = ruta_modelo

    # =====================================
    # CREAR SECUENCIAS
    # =====================================

    def _crear_secuencias(
        self,
        dataset
    ):

        X = []
        y = []

        # =====================================
        # ORDENAR POR FECHA
        # =====================================

        dataset = dataset.sort_values(
            "Fecha"
        ).copy()

        # =====================================
        # SEPARAR POR AÑO
        # =====================================

        for _, grupo in dataset.groupby(
            dataset["Fecha"].dt.year
        ):

            grupo = grupo.sort_values(
                "Fecha"
            ).copy()

            # Necesitamos al menos 25 observaciones
            if len(grupo) <= self.sequence_length:
                continue

            variables = grupo[
                FEATURES_LSTM
            ].values

            ventas = grupo[
                "ventas"
            ].values

            # =================================
            # CREAR SECUENCIAS
            # =================================

            for i in range(
                self.sequence_length,
                len(grupo)
            ):

                X.append(
                    variables[
                        i - self.sequence_length:i
                    ]
                )

                y.append(
                    ventas[i]
                )

        return (
            np.array(X),
            np.array(y)
        )

    def _crear_secuencias_continuas(
        self,
        dataset
    ):

        X = []
        y = []

        dataset = dataset.sort_values(
            "Fecha"
        ).copy()

        variables = dataset[
            FEATURES_LSTM
        ].values

        ventas = dataset[
            "ventas"
        ].values

        for i in range(
            self.sequence_length,
            len(dataset)
        ):

            X.append(
                variables[
                    i - self.sequence_length:i
                ]
            )

            y.append(
                ventas[i]
            )

        return (
            np.array(X),
            np.array(y)
        )

    # =====================================
    # CREAR UNA ÚNICA SECUENCIA
    # =====================================

    def crear_secuencia(
        self,
        dataset
    ):

        X = dataset[
            FEATURES_LSTM
        ].values

        X = self.scaler_X.transform(
            X
        )

        return X.reshape(
            1,
            self.sequence_length,
            N_FEATURES
        )
    
    # =====================================
    # ESCALAR DATOS
    # =====================================

    
    def _escalar(
        self,
        X_train,
        X_test,
        y_train,
        y_test
    ):

        n_train, pasos, variables = X_train.shape
        n_test = X_test.shape[0]

        # -------------------------------------
        # Escalar X
        # -------------------------------------

        X_train = X_train.reshape(-1, variables)
        X_test = X_test.reshape(-1, variables)

        X_train = self.scaler_X.fit_transform(
            X_train
        )

        X_test = self.scaler_X.transform(
            X_test
        )

        X_train = X_train.reshape(
            n_train,
            pasos,
            variables
        )

        X_test = X_test.reshape(
            n_test,
            pasos,
            variables
        )

        # -------------------------------------
        # Escalar Y
        # -------------------------------------

        y_train = self.scaler_y.fit_transform(
            y_train.reshape(-1, 1)
        )

        y_test = self.scaler_y.transform(
            y_test.reshape(-1, 1)
        )

        return (
            X_train,
            X_test,
            y_train,
            y_test
        )

    # =====================================
    # CONSTRUIR MODELO
    # =====================================

    def _construir_modelo(
        self,
        n_variables
    ):

        self.model = Sequential()

        self.model.add(

            LSTM(

                64,

                input_shape=(

                    self.sequence_length,

                    n_variables

                ),

                return_sequences=True

            )

        )

        self.model.add(

            Dropout(
                0.2
            )

        )

        self.model.add(

            LSTM(
                32
            )

        )

        self.model.add(

            Dropout(
                0.2
            )

        )

        self.model.add(

            Dense(
                16,
                activation="relu"
            )

        )

        self.model.add(

            Dense(
                1
            )

        )

        self.model.compile(

            optimizer="adam",

            loss="mse",

            metrics=["mae"]

        )

    # =====================================
    # ENTRENAR
    # =====================================

    def entrenar(self):

        # -------------------------
        # Train / Test
        # -------------------------

        self.separar_train_test()

        train = self.dataset.loc[
            self.X_train.index
        ].copy()

        test = self.dataset.loc[
            self.X_test.index
        ].copy()

        train = train.sort_values(
            "Fecha"
        ).copy()

        test = test.sort_values(
            "Fecha"
        ).copy()

        # =====================================
        # CREAR SECUENCIAS
        # =====================================

        if TIPO_SPLIT == "mensual":

            # ---------------------------------
            # COMPORTAMIENTO ORIGINAL
            # ---------------------------------

            X_train, y_train = self._crear_secuencias_continuas(
                train
            )

            X_test, y_test = self._crear_secuencias_continuas(
                test
            )

            self.test = test.iloc[
                self.sequence_length:
            ].copy()

            self.train = train.iloc[
                self.sequence_length:
            ].copy()


        elif TIPO_SPLIT == "temporal":

            # ---------------------------------
            # TRAIN
            # ---------------------------------

            X_train, y_train = self._crear_secuencias(
                train
            )

            # ---------------------------------
            # ÚLTIMAS 24 HORAS DEL TRAIN
            # COMO CONTEXTO DEL TEST
            # ---------------------------------

            contexto = train.iloc[
                -self.sequence_length:
            ].copy()

            # ---------------------------------
            # CONTEXTO + TEST
            # ---------------------------------

            test_con_contexto = pd.concat(
                [
                    contexto,
                    test
                ],
                ignore_index=True
            )

            # ---------------------------------
            # SECUENCIAS TEST
            # ---------------------------------

            X_test, y_test = self._crear_secuencias(
                test_con_contexto
            )

            # ---------------------------------
            # REFERENCIAS
            # ---------------------------------

            self.train = train.iloc[
                self.sequence_length:
            ].copy()

            self.test = test.iloc[
                self.sequence_length:
            ].copy()

        else:
 
            raise ValueError(
                f"TIPO_SPLIT desconocido: {TIPO_SPLIT}"
            )

        # =====================================
        # ESCALAR
        # =====================================

        X_train, X_test, y_train, y_test = self._escalar(

            X_train,
            X_test,

            y_train,
            y_test

        )

        # =====================================
        # GUARDAR
        # =====================================

        self.X_train = X_train
        self.X_test = X_test

        self.y_train = y_train
        self.y_test = y_test

        # =====================================
        # MODELO
        # =====================================

        self._construir_modelo(
            N_FEATURES
        )

        # =====================================
        # EARLY STOPPING
        # =====================================

        early = EarlyStopping(

            monitor="val_loss",

            patience=15,

            restore_best_weights=True

        )

        # =====================================
        # ENTRENAMIENTO
        # =====================================

        self.model.fit(

            self.X_train,

            self.y_train,

            validation_data=(

                self.X_test,

                self.y_test

            ),

            epochs=200,

            batch_size=32,

            callbacks=[early],

            verbose=1

        )

        print()

        print(
            "LSTM entrenada correctamente."
        )

        # =====================================
        # GUARDAR MODELO
        # =====================================

        # =====================================
        # RUTA DE GUARDADO
        # =====================================

        if self.ruta_modelo is not None:

            self.ruta_modelo.mkdir(
                parents=True,
                exist_ok=True
            )

            ruta_modelo = (
                self.ruta_modelo
                / "modelo_lstm.keras"
            )

            ruta_scaler_X = (
                self.ruta_modelo
                / "scaler_X.pkl"
            )

            ruta_scaler_y = (
                self.ruta_modelo
                / "scaler_y.pkl"
            )

        else:

            MODELS_PATH = (
                Path(__file__).resolve().parent
            )

            ruta_modelo = (
                MODELS_PATH
                / "modelo_lstm.keras"
            )

            ruta_scaler_X = (
                MODELS_PATH
                / "scaler_X.pkl"
            )

            ruta_scaler_y = (
                MODELS_PATH
                / "scaler_y.pkl"
            )


        # =====================================
        # GUARDAR
        # =====================================

        self.model.save(
            ruta_modelo
        )

        joblib.dump(
            self.scaler_X,
            ruta_scaler_X
        )

        joblib.dump(
            self.scaler_y,
            ruta_scaler_y
        )

        print(
            "Modelo y scalers guardados."
        )


    # =====================================
    # PREDECIR
    # =====================================

    def predecir(self):

        pred = self.model.predict(

            self.X_test,

            verbose=0

        )

        pred = self.scaler_y.inverse_transform(
            pred
        )

        self.predicciones = pred.ravel()

        self.y_test = self.scaler_y.inverse_transform(

            self.y_test

        ).ravel()

    # =====================================
    # IMPORTANCIA VARIABLES
    # =====================================

    def importancia_variables(self):

        print()

        print("========================")
        print("IMPORTANCIA VARIABLES")
        print("========================")

        print()

        