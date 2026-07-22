"""
Módulo que implementa el modelo de predicción basado en XGBoost.

Hereda la funcionalidad común definida en la clase base y se encarga de
configurar, entrenar y almacenar un modelo de regresión basado en XGBoost
para estimar las ventas a partir de las variables operativas y
contextuales del establecimiento.
"""

from .mod_model_base import ModelBase

from xgboost import XGBRegressor


class XGBoostModel(ModelBase):
    """
    Implementación del modelo XGBoost para la predicción de ventas.

    Configura y entrena un modelo de regresión basado en XGBoost utilizando
    el conjunto de datos preparado previamente. Una vez finalizado el
    entrenamiento, el modelo queda disponible para su evaluación y se
    almacena para su posterior utilización en el proceso de predicción.
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

        self.model = XGBRegressor(

            n_estimators=300,

            max_depth=6,

            learning_rate=0.05,

            subsample=0.8,

            colsample_bytree=0.8,

            random_state=42,

            objective="reg:squarederror",

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

        import joblib

        print(
            "XGBoost entrenado correctamente."
        )

        joblib.dump(
            self.model,
            "modelo_xgboost.pkl"
        )

        print("Modelo guardado.")
