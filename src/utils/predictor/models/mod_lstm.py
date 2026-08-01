"""
Módulo que implementa un modelo de predicción basado en redes neuronales LSTM.

La red aprende patrones temporales utilizando secuencias de observaciones
horarias consecutivas para estimar las ventas de la hora siguiente.
"""

from pathlib import Path

import joblib
import numpy as np

from sklearn.preprocessing import MinMaxScaler

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    LSTM,
    Dense,
    Dropout
)
from tensorflow.keras.callbacks import EarlyStopping

from .mod_model_base import ModelBase


SEQUENCE_LENGTH = 24

FEATURES_LSTM = [
    "ventas"
]


class LSTMModel(ModelBase):

    def __init__(
        self,
        dataset
    ):

        super().__init__(dataset)

        self.scaler_X = MinMaxScaler()

        self.scaler_y = MinMaxScaler()

        self.sequence_length = SEQUENCE_LENGTH

    # =====================================
    # CREAR SECUENCIAS
    # =====================================

    def _crear_secuencias(
        self,
        dataset
    ):

        X = []
        y = []

        ventas = dataset["ventas"].values.reshape(-1, 1)

        for i in range(self.sequence_length, len(dataset)):

            X.append(
                ventas[i-self.sequence_length:i]
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

        X = dataset["ventas"].values.reshape(-1, 1)

        return X.reshape(

            1,

            self.sequence_length,

            len(FEATURES_LSTM)

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

        # -------------------------
        # Crear secuencias
        # -------------------------

        X_train, y_train = self._crear_secuencias(
            train
        )

        X_test, y_test = self._crear_secuencias(
            test
        )

        # -------------------------
        # Ajustar test
        # -------------------------

        self.test = test.iloc[
            self.sequence_length:
        ].copy()


        # -------------------------
        # Escalar
        # -------------------------

        X_train, X_test, y_train, y_test = self._escalar(

            X_train,
            X_test,

            y_train,
            y_test

        )

        self.X_train = X_train
        self.X_test = X_test

        self.y_train = y_train
        self.y_test = y_test


        # -------------------------
        # Modelo
        # -------------------------

        self._construir_modelo(
            X_train.shape[2]
        )

        # -------------------------
        # Early stopping
        # -------------------------

        early = EarlyStopping(

            monitor="val_loss",

            patience=15,

            restore_best_weights=True

        )

        # -------------------------
        # Entrenamiento
        # -------------------------

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

        MODELS_PATH = Path(__file__).resolve().parent

        self.model.save(
            MODELS_PATH / "modelo_lstm.keras"
        )

        joblib.dump(
            self.scaler_X,
            MODELS_PATH / "scaler_X.pkl"
        )

        joblib.dump(
            self.scaler_y,
            MODELS_PATH / "scaler_y.pkl"
        )

        print(
            "Modelo guardado."
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

        print(
            "Las redes neuronales LSTM no disponen de una "
            "importancia de variables directa."
        )