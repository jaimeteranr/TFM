"""
Módulo encargado de validar modelos de predicción mediante la estrategia
Walk-Forward.

Evalúa el rendimiento del modelo simulando un escenario real de predicción,
entrenándolo de forma progresiva con la información histórica disponible y
evaluándolo sobre periodos temporales posteriores. Este procedimiento
permite analizar la capacidad de generalización del modelo en un contexto
cronológico.
"""

import pandas as pd

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


class WalkForwardValidator:
    """
    Valida modelos de predicción mediante una estrategia Walk-Forward.

    Ejecuta sucesivos procesos de entrenamiento y evaluación utilizando
    particiones temporales de los datos, recopilando las métricas obtenidas
    en cada periodo para analizar el comportamiento y la estabilidad del
    modelo a lo largo del tiempo.
    """


    def __init__(

        self,

        dataset,

        model_class,

        features,

        target="ventas"

    ):

        self.dataset = dataset.copy()

        self.model_class = model_class

        self.features = features

        self.target = target

        self.resultados = []


    def validar(self):

        # =====================================
        # MESES DISPONIBLES
        # =====================================

        meses = (

            self.dataset[["Fecha"]]

            .assign(

                año=lambda x: x["Fecha"].dt.year,

                mes=lambda x: x["Fecha"].dt.month

            )

            .drop_duplicates(

                ["año", "mes"]

            )

            .sort_values(

                ["año", "mes"]

            )

            .reset_index(drop=True)

        )

        # =====================================
        # DESDE EL SEGUNDO MES
        # =====================================

        for i in range(1, len(meses)):

            año_test = meses.loc[i, "año"]

            mes_test = meses.loc[i, "mes"]

            fecha_inicio = pd.Timestamp(

                year=año_test,

                month=mes_test,

                day=1

            )

            fecha_fin = fecha_inicio + pd.offsets.MonthEnd(1)

            train = self.dataset[

                self.dataset["Fecha"] < fecha_inicio

            ].copy()

            test = self.dataset[

                (self.dataset["Fecha"] >= fecha_inicio)

                &

                (self.dataset["Fecha"] <= fecha_fin)

            ].copy()

            if len(train) == 0 or len(test) == 0:

                continue

            X_train = train[self.features]

            y_train = train[self.target]

            X_test = test[self.features]

            y_test = test[self.target]

            modelo = self.model_class(

                self.dataset

            )

            modelo.entrenar(

                X_train,

                y_train,

                X_test,

                y_test

            )

            modelo.predecir()

            mae = mean_absolute_error(

                y_test,

                modelo.predicciones

            )

            mse = mean_squared_error(

                y_test,

                modelo.predicciones

            )

            rmse = mse ** 0.5

            r2 = r2_score(

                y_test,

                modelo.predicciones

            )

            self.resultados.append({

                "Año": año_test,

                "Mes": mes_test,

                "Train": len(train),

                "Test": len(test),

                "MAE": mae,

                "RMSE": rmse,

                "R2": r2

            })

        self.resultados = pd.DataFrame(

            self.resultados

        )

        return self.resultados


    def resumen(self):

        print()

        print("========================")

        print("WALK FORWARD")

        print("========================")

        print()

        print(self.resultados)

        print()

        print("------------------------")

        print("MEDIA")

        print("------------------------")

        print()

        print(

            f"MAE : {self.resultados['MAE'].mean():.2f}"

        )

        print(

            f"RMSE: {self.resultados['RMSE'].mean():.2f}"

        )

        print(

            f"R²  : {self.resultados['R2'].mean():.4f}"

        )

        print()

        print("------------------------")

        print("MEJOR MES")

        print("------------------------")

        mejor = self.resultados.loc[

            self.resultados["MAE"].idxmin()

        ]

        print(mejor)

        print()

        print("------------------------")

        print("PEOR MES")

        print("------------------------")

        peor = self.resultados.loc[

            self.resultados["MAE"].idxmax()

        ]

        print(peor)