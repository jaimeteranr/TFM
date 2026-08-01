"""
Módulo auxiliar para la optimización del modelo Random Forest.

Evalúa distintas combinaciones de hiperparámetros mediante el entrenamiento
de múltiples modelos y compara su rendimiento utilizando diferentes métricas
de regresión, facilitando la selección de la configuración más adecuada.
"""

import pandas as pd

from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


class RandomForestOptimizer:
    """
    Optimiza la configuración del modelo Random Forest.

    Entrena y evalúa diferentes combinaciones de hiperparámetros sobre un
    mismo conjunto de entrenamiento y prueba, generando un resumen
    comparativo de los resultados que permite identificar la configuración
    con mejor rendimiento.
    """

    def __init__(
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

    def optimizar(self):

        # =====================================
        # PARÁMETROS A PROBAR
        # =====================================

        parametros = [

            (300, 15, 1),
            (300, 15, 2),
            (300, 15, 5),

            (500, 15, 1),
            (500, 15, 2),
            (500, 15, 5),

            (300, 20, 1),
            (300, 20, 2),
            (300, 20, 5),

            (500, 20, 1),
            (500, 20, 2),
            (500, 20, 5)

        ]

        resultados = []

        print("\n========================")
        print("OPTIMIZACIÓN RANDOM FOREST")
        print("========================\n")

        # =====================================
        # BUCLE
        # =====================================

        for (
            n_estimators,
            max_depth,
            min_samples_leaf
        ) in parametros:

            modelo = RandomForestRegressor(

                n_estimators=n_estimators,

                max_depth=max_depth,

                min_samples_leaf=min_samples_leaf,

                random_state=42,

                n_jobs=-1

            )

            modelo.fit(

                self.X_train,

                self.y_train

            )

            predicciones = modelo.predict(

                self.X_test

            )

            mae = mean_absolute_error(

                self.y_test,

                predicciones

            )

            mse = mean_squared_error(

                self.y_test,

                predicciones

            )

            rmse = mse ** 0.5

            r2 = r2_score(

                self.y_test,

                predicciones

            )

            resultados.append({

                "Árboles": n_estimators,

                "Profundidad": max_depth,

                "Min Leaf": min_samples_leaf,

                "MAE": round(mae, 2),

                "RMSE": round(rmse, 2),

                "R2": round(r2, 4)

            })

            print(

                f"Árboles={n_estimators} | "
                f"Prof={max_depth} | "
                f"Leaf={min_samples_leaf} "
                f"-> MAE={mae:.2f} "
                f"RMSE={rmse:.2f} "
                f"R²={r2:.4f}"

            )

        # =====================================
        # RESULTADOS
        # =====================================

        resultados = pd.DataFrame(resultados)

        resultados = resultados.sort_values(

            by="RMSE"

        ).reset_index(drop=True)

        print("\n========================")
        print("RANKING FINAL")
        print("========================\n")

        print(resultados)

        print("\n========================")
        print("MEJOR CONFIGURACIÓN")
        print("========================\n")

        print(resultados.iloc[0])

        return resultados