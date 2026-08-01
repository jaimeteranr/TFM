"""
Módulo encargado de la representación gráfica del conjunto de datos.

Genera distintas visualizaciones que permiten analizar de forma intuitiva la
relación entre las ventas y las variables explicativas, así como estudiar su
distribución y evolución temporal antes del entrenamiento de los modelos de
predicción.
"""

import matplotlib.pyplot as plt


class DatasetVisualizer:
    """
    Genera representaciones gráficas del conjunto de datos.

    Proporciona un conjunto de visualizaciones orientadas al análisis
    exploratorio de la información, facilitando la identificación de
    patrones, tendencias y relaciones entre las ventas y las principales
    variables del sistema.
    """

    def __init__(
        self,
        dataset
    ):

        self.dataset = dataset

    def visualizar(self):

        dataset = self.dataset

        print("\n========================")
        print("ANÁLISIS GRÁFICO")
        print("========================")

        # ============================
        # Ventas vs temperatura
        # ============================

        plt.figure(figsize=(8,5))

        plt.scatter(
            dataset["temperatura_celsius"],
            dataset["ventas"]
        )

        plt.xlabel("Temperatura (ºC)")
        plt.ylabel("Ventas (€)")
        plt.title("Ventas vs temperatura")

        plt.grid()

        plt.show()

        # ============================
        # Ventas vs lluvia
        # ============================

        plt.figure(figsize=(8,5))

        plt.scatter(
            dataset["lluvia_mm"],
            dataset["ventas"]
        )

        plt.xlabel("Lluvia (mm)")
        plt.ylabel("Ventas (€)")
        plt.title("Ventas vs lluvia")

        plt.grid()

        plt.show()

        # ============================
        # Ventas vs viento
        # ============================

        plt.figure(figsize=(8,5))

        plt.scatter(
            dataset["viento_km_h"],
            dataset["ventas"]
        )

        plt.xlabel("Viento (km/h)")
        plt.ylabel("Ventas (€)")
        plt.title("Ventas vs viento")

        plt.grid()

        plt.show()

        # ============================
        # Ventas vs nubosidad
        # ============================

        plt.figure(figsize=(8,5))

        plt.scatter(
            dataset["nubosidad_porcentaje"],
            dataset["ventas"]
        )

        plt.xlabel("Nubosidad (%)")
        plt.ylabel("Ventas (€)")
        plt.title("Ventas vs nubosidad")

        plt.grid()

        plt.show()

        # ============================
        # Ventas por hora
        # ============================

        medias = dataset.groupby(
            "hora"
        )["ventas"].mean()

        plt.figure(figsize=(10,5))

        medias.plot(kind="bar")

        plt.ylabel("Ventas medias (€)")
        plt.title("Ventas medias por hora")

        plt.grid(axis="y")

        plt.show()

        # ============================
        # Ventas por día semana
        # ============================

        medias = dataset.groupby(
            "dia_semana_nombre"
        )["ventas"].mean()

        plt.figure(figsize=(8,5))

        medias.plot(kind="bar")

        plt.ylabel("Ventas medias (€)")
        plt.title("Ventas medias por día de la semana")

        plt.grid(axis="y")

        plt.show()

        # ============================
        # Ventas por Weather Code
        # ============================

        medias = dataset.groupby(
            "weather_code"
        )["ventas"].mean()

        plt.figure(figsize=(8,5))

        medias.plot(kind="bar")

        plt.ylabel("Ventas medias (€)")
        plt.title("Ventas medias según Weather Code")

        plt.grid(axis="y")

        plt.show()

        # ============================
        # Evolución temporal
        # ============================

        plt.figure(figsize=(14,5))

        plt.plot(
            dataset["datetime"],
            dataset["ventas"]
        )

        plt.xlabel("Fecha")
        plt.ylabel("Ventas (€)")
        plt.title("Evolución temporal de las ventas")

        plt.grid()

        plt.show()