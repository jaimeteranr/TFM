"""
Módulo que implementa el modelo de predicción basado en Random Forest.

Hereda la funcionalidad común definida en la clase base y se encarga de
configurar y entrenar un modelo de regresión basado en bosques aleatorios
para estimar las ventas a partir de las variables operativas y
contextuales del establecimiento.
"""

from .mod_model_base import ModelBase

from sklearn.ensemble import RandomForestRegressor


class RandomForestModel(ModelBase):
    """
    Implementación del modelo Random Forest para la predicción de ventas.

    Configura y entrena un modelo de regresión basado en bosques aleatorios
    utilizando el conjunto de datos preparado previamente. Una vez
    entrenado, el modelo puede emplearse para realizar predicciones y
    evaluar su rendimiento sobre datos no utilizados durante el
    entrenamiento.
    """
    
    def __init__(
        self,
        dataset
    ):

        super().__init__(dataset)

    def entrenar(

        self,

        X_train=None,
        y_train=None,

        X_test=None,
        y_test=None

    ):

        # =====================================
        # TRAIN / TEST
        # =====================================

        if X_train is None:

            self.separar_train_test()

        else:

            self.asignar_train_test(

                X_train,
                y_train,

                X_test,
                y_test

            )

        # =====================================
        # MODELO
        # =====================================

        self.model = RandomForestRegressor(

            n_estimators=300,

            max_depth=15,

            random_state=42,

            n_jobs=-1

        )

        # =====================================
        # ENTRENAMIENTO
        # =====================================

        self.model.fit(

            self.X_train,

            self.y_train

        )

        print()

        print("Random Forest entrenado correctamente.")