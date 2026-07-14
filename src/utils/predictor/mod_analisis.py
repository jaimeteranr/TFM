import matplotlib.pyplot as plt


class DatasetVisualizer:

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
        # Beneficio vs temperatura
        # ============================

        plt.figure(figsize=(8,5))

        plt.scatter(
            dataset["temp_apertura"],
            dataset["Beneficio"]
        )

        plt.xlabel("Temperatura apertura (ºC)")
        plt.ylabel("Beneficio (€)")
        plt.title("Beneficio vs temperatura apertura")

        plt.grid()

        plt.show()

        # ============================
        # Beneficio vs lluvia
        # ============================

        plt.figure(figsize=(8,5))

        plt.scatter(
            dataset["lluvia_total"],
            dataset["Beneficio"]
        )

        plt.xlabel("Lluvia (mm)")
        plt.ylabel("Beneficio (€)")
        plt.title("Beneficio vs lluvia")

        plt.grid()

        plt.show()

        # ============================
        # Beneficio vs viento
        # ============================

        plt.figure(figsize=(8,5))

        plt.scatter(
            dataset["viento_medio"],
            dataset["Beneficio"]
        )

        plt.xlabel("Viento (km/h)")
        plt.ylabel("Beneficio (€)")
        plt.title("Beneficio vs viento")

        plt.grid()

        plt.show()

        # ============================
        # Beneficio vs nubosidad
        # ============================

        plt.figure(figsize=(8,5))

        plt.scatter(
            dataset["nubosidad_media"],
            dataset["Beneficio"]
        )

        plt.xlabel("Nubosidad (%)")
        plt.ylabel("Beneficio (€)")
        plt.title("Beneficio vs nubosidad")

        plt.grid()

        plt.show()

        # ============================
        # Beneficio por día semana
        # ============================

        medias = dataset.groupby(
            "dia_semana"
        )["Beneficio"].mean()

        plt.figure(figsize=(8,5))

        medias.plot(kind="bar")

        plt.ylabel("Beneficio medio (€)")
        plt.title("Beneficio medio por día")

        plt.grid(axis="y")

        plt.show()

        # ============================
        # Beneficio por weather code
        # ============================

        medias = dataset.groupby(
            "weather_code"
        )["Beneficio"].mean()

        plt.figure(figsize=(8,5))

        medias.plot(kind="bar")

        plt.ylabel("Beneficio medio (€)")
        plt.title("Beneficio medio según Weather Code")

        plt.grid(axis="y")

        plt.show()

        # ============================
        # Beneficio por mes
        # ============================

        dataset["mes"] = dataset["Fecha"].dt.month

        medias = dataset.groupby(
            "mes"
        )["Beneficio"].mean()

        plt.figure(figsize=(8,5))

        medias.plot(kind="bar")

        plt.ylabel("Beneficio medio (€)")
        plt.title("Beneficio medio por mes")

        plt.grid(axis="y")

        plt.show()