"""
Módulo que implementa el modelo de predicción basado en árboles de decisión.

Hereda la funcionalidad común definida en la clase base y se encarga de
configurar y entrenar un modelo de regresión basado en árboles de decisión.
Además, incorpora herramientas para representar gráficamente la estructura
del árbol y facilitar la interpretación del modelo.
"""

from .mod_model_base import ModelBase

from sklearn.tree import (
    DecisionTreeRegressor,
    plot_tree
)

import matplotlib.pyplot as plt


class DecisionTreeModel(ModelBase):
    """
    Implementación del modelo de regresión mediante árboles de decisión.

    Configura y entrena un árbol de decisión utilizando el conjunto de datos
    preparado previamente. Asimismo, permite visualizar la estructura del
    modelo entrenado para facilitar el análisis de las reglas de decisión
    aprendidas.
    """

    def __init__(
        self,
        dataset
    ):

        super().__init__(
            dataset
        )

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

            self.preparar_train_test()

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

        self.model = DecisionTreeRegressor(

            random_state=42,

            max_depth=10,

            min_samples_split=20,

            min_samples_leaf=10

        )

        # =====================================
        # ENTRENAMIENTO
        # =====================================

        self.model.fit(

            self.X_train,

            self.y_train

        )

        print()

        print(
            "Árbol entrenado correctamente."
        )

    # =====================================
    # DIBUJAR ÁRBOL
    # =====================================

    def dibujar_arbol(
        self,
        profundidad=4
    ):

        plt.figure(

            figsize=(24, 12)

        )

        plot_tree(

            self.model,

            feature_names=self.FEATURES,

            filled=True,

            rounded=True,

            max_depth=profundidad,

            fontsize=8

        )

        plt.title(
            "Decision Tree"
        )

        plt.show()