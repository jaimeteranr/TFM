"""
Funciones de visualización para comparar el comportamiento de los distintos
modelos de predicción de ventas.
"""

import matplotlib.pyplot as plt
import numpy as np


def comparar_modelos(
    modelos,
    nombres=None,
    n=250
):

    y_real = np.asarray(
        modelos[0].y_test
    ).ravel()

    if nombres is None:

        nombres = [

            type(modelo).__name__

            for modelo in modelos

        ]

    # =====================================
    # NÚMERO DE OBSERVACIONES DISPONIBLES
    # =====================================

    n_disponible = min(
        len(modelo.test)
        for modelo in modelos
    )

    n_real = min(
        n,
        n_disponible
    )

    print(
        f"Observaciones utilizadas: "
        f"{n_real} de {n_disponible} disponibles"
    )

    tam_bloque = 50

    for inicio in range(
        0,
        n_real,
        tam_bloque
    ):

        fin = min(
            inicio + tam_bloque,
            n_real
        )

        fecha_inicio = modelos[0].test.iloc[inicio]["Fecha"]
        hora_inicio = modelos[0].test.iloc[inicio]["Hora"]

        fecha_fin = modelos[0].test.iloc[fin - 1]["Fecha"]
        hora_fin = modelos[0].test.iloc[fin - 1]["Hora"]

        plt.figure(figsize=(16,5))
        plt.plot(
            range(inicio, fin),
            y_real[inicio:fin],
            linewidth=3,
            color="black",
            label="Ventas reales"
        )

        for modelo, nombre in zip(modelos, nombres):

            plt.plot(
                range(inicio, fin),
                np.asarray(modelo.predicciones).ravel()[inicio:fin],
                label=nombre
            )

        plt.title(
            f"Observaciones {inicio}-{fin-1} | "
            f"{fecha_inicio.strftime('%d/%m/%Y')} {hora_inicio} → "
            f"{fecha_fin.strftime('%d/%m/%Y')} {hora_fin}"
        )
        plt.xlabel("Observación")
        plt.ylabel("Ventas")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

# =====================================
# COMPARAR MODELOS - TRAIN
# =====================================

def comparar_modelos_train(
    modelos,
    nombres=None,
    semanas=3
):

    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    # =====================================
    # NOMBRES
    # =====================================

    if nombres is None:

        nombres = [

            type(modelo).__name__

            for modelo in modelos

        ]

    # =====================================
    # COMPROBAR MODELOS
    # =====================================

    if len(modelos) != len(nombres):

        raise ValueError(
            "El número de modelos y nombres debe coincidir."
        )

    # =====================================
    # DATOS TRAIN
    # =====================================

    train = modelos[0].train.copy()

    train["año"] = train["Fecha"].dt.year

    train["semana"] = (
        train["Fecha"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    # =====================================
    # SEMANAS DISPONIBLES
    # =====================================

    semanas_disponibles = (

        train[
            ["año", "semana"]
        ]

        .drop_duplicates()

        .sort_values(
            ["año", "semana"]
        )

    )

    # =====================================
    # SELECCIONAR SEMANAS
    # =====================================

    semanas_seleccionadas = (
        semanas_disponibles
        .head(semanas)
    )

    print()
    print("========================")
    print("VISUALIZACIÓN TRAIN")
    print("========================")
    print()

    print(
        "Semanas seleccionadas:"
    )

    print(
        semanas_seleccionadas
    )

    # =====================================
    # REFERENCIA TRAIN
    # =====================================

    # La LSTM pierde las primeras 24 filas porque
    # necesita una ventana inicial para construir
    # la primera secuencia.

    modelo_lstm = None

    for modelo, nombre in zip(
        modelos,
        nombres
    ):

        if nombre == "LSTM":

            modelo_lstm = modelo

            break


    # =====================================
    # DATASET DE REFERENCIA
    # =====================================

    if modelo_lstm is not None:

        train_referencia = (
            modelo_lstm.train.copy()
        )

    else:

        train_referencia = (
            modelos[0].train.copy()
        )


    # =====================================
    # PREDICCIONES
    # =====================================

    predicciones = {}


    for modelo, nombre in zip(
        modelos,
        nombres
    ):

        print(
            f"Generando predicciones TRAIN - {nombre}"
        )

        # =================================
        # LSTM
        # =================================

        if nombre == "LSTM":

            pred = modelo.model.predict(
                modelo.X_train,
                verbose=0
            )

            pred = modelo.scaler_y.inverse_transform(
                pred
            ).ravel()

        # =================================
        # RESTO DE MODELOS
        # =================================

        else:

            # Índices correspondientes a las
            # filas que utiliza la LSTM

            indices = train_referencia.index

            X = modelo.X_train.loc[
                indices
            ]

            pred = modelo.model.predict(
                X
            )

            pred = np.asarray(
                pred
            ).ravel()

        predicciones[nombre] = pred


    # =====================================
    # CONSTRUIR RESULTADOS
    # =====================================

    resultados = train_referencia[
        [
            "Fecha",
            "Hora",
            "ventas"
        ]
    ].copy()


    resultados = resultados.rename(
        columns={
            "ventas": "Venta real"
        }
    )


    # =====================================
    # AÑADIR PREDICCIONES
    # =====================================

    for nombre in nombres:

        pred = predicciones[
            nombre
        ]

        if len(pred) != len(resultados):

            raise ValueError(
                f"El modelo {nombre} tiene "
                f"{len(pred)} predicciones, "
                f"pero el train de referencia tiene "
                f"{len(resultados)} filas."
            )

        resultados[nombre] = pred

    # =====================================
    # AÑO / SEMANA
    # =====================================

    resultados["año"] = (
        resultados["Fecha"]
        .dt.year
    )

    resultados["semana"] = (
        resultados["Fecha"]
        .dt.isocalendar()
        .week
            .astype(int)
    )

    # =====================================
    # GRÁFICOS
    # =====================================

    for _, fila in semanas_seleccionadas.iterrows():

        año = fila["año"]

        semana = fila["semana"]

        datos = resultados[
            (resultados["año"] == año)
            &
            (resultados["semana"] == semana)
        ].copy()

        if datos.empty:

            continue

        # -------------------------
        # GRÁFICO
        # -------------------------

        plt.figure(
            figsize=(16, 6)
        )

        # -------------------------
        # VENTAS REALES
        # -------------------------

        plt.plot(
            range(len(datos)),
            datos["Venta real"],
            label="Ventas reales",
            linewidth=3,
            color="black"
        )

        # -------------------------
        # MODELOS
        # -------------------------

        for nombre in nombres:

            plt.plot(
                range(len(datos)),
                datos[nombre],
                label=nombre
            )

        # -------------------------
        # TÍTULO
        # -------------------------

        fecha_min = datos["Fecha"].min()

        fecha_max = datos["Fecha"].max()

        plt.title(
            f"TRAIN - Semana {semana} | "
            f"{fecha_min:%d/%m/%Y %H:%M} → "
            f"{fecha_max:%d/%m/%Y %H:%M}"
        )

        plt.xlabel(
            "Observación"
        )

        plt.ylabel(
            "Ventas"
        )

        plt.legend()

        plt.grid(
            True,
            alpha=0.3
        )

        plt.tight_layout()

        plt.show()