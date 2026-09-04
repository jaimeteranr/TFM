"""
Funciones de visualización para comparar el comportamiento de los distintos
modelos de predicción de ventas.
"""

import matplotlib.pyplot as plt
import numpy as np


def comparar_modelos(
    modelos,
    nombres=None,
    n=None
):

    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    # =====================================
    # NOMBRES
    # =====================================

    if nombres is None:

        nombres = [
            type(modelo).__name__
            for modelo in modelos
        ]

    if len(modelos) != len(nombres):

        raise ValueError(
            "El número de modelos y nombres debe coincidir."
        )

    # =====================================
    # MODELO DE REFERENCIA
    # =====================================

    modelo = modelos[0]

    y_real = np.asarray(
        modelo.y_test
    ).ravel()

    test = modelo.test.copy()

    # =====================================
    # DATETIME
    # =====================================

    test["datetime"] = pd.to_datetime(
        test["Fecha"].astype(str)
        + " "
        + test["Hora"].astype(str)
    )

    # =====================================
    # ORDEN TEMPORAL
    # =====================================

    orden = np.argsort(
        test["datetime"].values
    )

    test = test.iloc[orden].copy()

    y_real = y_real[orden]

    # =====================================
    # SEMANAS DEL TEST
    # =====================================

    test["semana_inicio"] = (
        test["datetime"]
        -
        pd.to_timedelta(
            test["datetime"].dt.weekday,
            unit="D"
        )
    ).dt.normalize()

    semanas = (
        test["semana_inicio"]
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    print()
    print("========================")
    print("GRÁFICAS SEMANALES DEL TEST")
    print("========================")
    print()
    print(
        "Semanas a visualizar:",
        len(semanas)
    )

    # =====================================
    # RECORRER TODAS LAS SEMANAS
    # =====================================

    for semana_inicio in semanas:

        semana_fin = (
            semana_inicio
            + pd.Timedelta(days=7)
        )

        # ---------------------------------
        # DATOS DE ESTA SEMANA
        # ---------------------------------

        mascara_semana = (
            test["semana_inicio"]
            == semana_inicio
        )

        test_semana = test[
            mascara_semana
        ].copy()

        indices_semana = np.where(
            mascara_semana
        )[0]

        if len(test_semana) == 0:

            continue

        # =================================
        # FIGURA
        # =================================

        plt.figure(
            figsize=(18, 6)
        )

        # =================================
        # VENTAS REALES
        # =================================

        plt.plot(
            test_semana["datetime"],
            y_real[indices_semana],
            color="black",
            linewidth=2.5,
            label="Ventas reales"
        )

        # =================================
        # PREDICCIONES
        # =================================

        for modelo_actual, nombre in zip(
            modelos,
            nombres
        ):

            pred = np.asarray(
                modelo_actual.predicciones
            ).ravel()

            test_modelo = modelo_actual.test.copy()

            # ---------------------------------
            # Alinear predicción / test
            # ---------------------------------

            if len(pred) < len(test_modelo):

                test_modelo = test_modelo.iloc[
                    len(test_modelo) - len(pred):
                ].copy()

            elif len(pred) > len(test_modelo):

                pred = pred[
                    :len(test_modelo)
                ]

            # ---------------------------------
            # DATETIME
            # ---------------------------------

            test_modelo["datetime"] = pd.to_datetime(
                test_modelo["Fecha"].astype(str)
                + " "
                + test_modelo["Hora"].astype(str)
            )

            # ---------------------------------
            # ORDEN TEMPORAL
            # ---------------------------------

            orden_modelo = np.argsort(
                test_modelo["datetime"].values
            )

            test_modelo = test_modelo.iloc[
                orden_modelo
            ].copy()

            pred = pred[
                orden_modelo
            ]

            # ---------------------------------
            # SEMANA
            # ---------------------------------

            mascara_modelo = (
                (
                    test_modelo["datetime"]
                    >= semana_inicio
                )
                &
                (
                    test_modelo["datetime"]
                    < semana_fin
                )
            )

            if not mascara_modelo.any():

                continue

            plt.plot(
                test_modelo.loc[
                    mascara_modelo,
                    "datetime"
                ],
                pred[
                    mascara_modelo.values
                ],
                linewidth=1.5,
                label=nombre
            )

        # =================================
        # LÍNEAS DE CAMBIO DE DÍA
        # =================================

        dias = pd.date_range(
            start=semana_inicio + pd.Timedelta(days=1),
            end=semana_fin - pd.Timedelta(days=1),
            freq="D"
        )

        for dia in dias:

            plt.axvline(
                dia,
                color="gray",
                linestyle="--",
                linewidth=0.8,
                alpha=0.7
            )

        # =================================
        # EJE X
        # =================================

        ax = plt.gca()

        ax.xaxis.set_major_locator(
            mdates.HourLocator(
                interval=3
            )
        )

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%d/%m %H:%M"
            )
        )

        plt.xticks(
            rotation=45,
            ha="right"
        )

        # =================================
        # TÍTULO
        # =================================

        fecha_ultima = (
            semana_fin
            - pd.Timedelta(
                hours=1
            )
        )

        semana_iso = (
            semana_inicio
            .isocalendar()
            .week
        )

        plt.title(
            f"Semana {semana_iso} | "
            f"{semana_inicio:%d/%m/%Y} → "
            f"{fecha_ultima:%d/%m/%Y}"
        )

        plt.xlabel(
            "Día y hora"
        )

        plt.ylabel(
            "Ventas"
        )

        plt.grid(
            True,
            alpha=0.25
        )

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

def mostrar_train_test_completo(
    modelos,
    nombres=None
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

    if len(modelos) != len(nombres):

        raise ValueError(
            "El número de modelos y nombres debe coincidir."
        )

    # =====================================
    # DATASET COMPLETO
    # =====================================

    modelo_referencia = modelos[0]

    train = modelo_referencia.train.copy()
    test = modelo_referencia.test.copy()

    # -------------------------------------
    # DATETIME
    # -------------------------------------

    def crear_datetime(df):

        df = df.copy()

        df["datetime"] = pd.to_datetime(
            df["Fecha"].astype(str)
            + " "
            + df["Hora"].astype(str)
        )

        return df

    train = crear_datetime(train)
    test = crear_datetime(test)

    # =====================================
    # TRAIN
    # =====================================

    train_completo = train[
        [
            "datetime",
            "ventas"
        ]
    ].copy()

    train_completo["tipo"] = "TRAIN"

    # =====================================
    # TEST
    # =====================================

    test_completo = test[
        [
            "datetime",
            "ventas"
        ]
    ].copy()

    test_completo["tipo"] = "TEST"

    # =====================================
    # UNIR TRAIN + TEST
    # =====================================

    datos = pd.concat(
        [
            train_completo,
            test_completo
        ],
        ignore_index=True
    )

    datos = (
        datos
        .sort_values(
            ["datetime", "tipo"]
        )
        .drop_duplicates(
            subset="datetime",
            keep="last"
        )
        .sort_values("datetime")
        .reset_index(drop=True)
    )

    # =====================================
    # PREDICCIONES
    # =====================================

    predicciones = {}

    for modelo, nombre in zip(
        modelos,
        nombres
    ):

        print()
        print(
            f"Generando predicciones TRAIN - {nombre}"
        )

        # =================================
        # PREDICCIONES TRAIN
        # =================================

        if nombre == "LSTM":

            pred_train = modelo.model.predict(
                modelo.X_train,
                verbose=0
            )

            pred_train = (
                modelo.scaler_y
                .inverse_transform(
                    pred_train
                )
                .ravel()
            )

            # La LSTM necesita una ventana
            # inicial de 24 observaciones.
            #
            # Por tanto, sus predicciones empiezan
            # más tarde que el train original.

            train_modelo = modelo.train.iloc[
                len(modelo.train) - len(pred_train):
            ].copy()

        else:

            pred_train = modelo.model.predict(
                modelo.X_train
            )

            pred_train = np.asarray(
                pred_train
            ).ravel()

            train_modelo = modelo.train.copy()

            # Seguridad por si hubiera alguna
            # diferencia de longitud.

            if len(pred_train) < len(train_modelo):

                train_modelo = train_modelo.iloc[
                    len(train_modelo) - len(pred_train):
                ].copy()

            elif len(pred_train) > len(train_modelo):

                pred_train = pred_train[
                    :len(train_modelo)
                ]

        train_modelo = crear_datetime(
            train_modelo
        )

        pred_train_df = pd.DataFrame({

            "datetime":
                train_modelo["datetime"].values,

            "prediccion":
                pred_train,

            "tipo":
                "TRAIN"

        })

        # =================================
        # PREDICCIONES TEST
        # =================================

        pred_test = np.asarray(
            modelo.predicciones
        ).ravel()

        test_modelo = modelo.test.copy()

        test_modelo = crear_datetime(
            test_modelo
        )

        # ---------------------------------
        # AJUSTE LSTM
        # ---------------------------------

        if len(pred_test) < len(test_modelo):

            test_modelo = test_modelo.iloc[
                len(test_modelo) - len(pred_test):
            ].copy()

        elif len(pred_test) > len(test_modelo):

            pred_test = pred_test[
                :len(test_modelo)
            ]

        pred_test_df = pd.DataFrame({

            "datetime":
                test_modelo["datetime"].values,

            "prediccion":
                pred_test,

            "tipo":
                "TEST"

        })

        # =================================
        # UNIR TRAIN + TEST
        # =================================

        pred_df = pd.concat(
            [
                pred_train_df,
                pred_test_df
            ],
            ignore_index=True
        )

        pred_df = (
            pred_df
            .sort_values(
                ["datetime", "tipo"]
            )
            .drop_duplicates(
                subset="datetime",
                keep="last"
            )
            .sort_values("datetime")
            .reset_index(drop=True)
        )

        predicciones[nombre] = pred_df

        print(
            f"  TRAIN: {len(pred_train_df)} predicciones"
        )

        print(
            f"  TEST : {len(pred_test_df)} predicciones"
        )

    # =====================================
    # SEMANA
    # =====================================

    datos["semana_inicio"] = (
        datos["datetime"]
        -
        pd.to_timedelta(
            datos["datetime"].dt.weekday,
            unit="D"
        )
    ).dt.normalize()

    # =====================================
    # INFORMACIÓN
    # =====================================

    print()
    print("========================")
    print("VISUALIZACIÓN TRAIN + TEST")
    print("========================")
    print()

    print(
        "Fecha inicial:",
        datos["datetime"].min()
    )

    print(
        "Fecha final:",
        datos["datetime"].max()
    )

    print(
        "Observaciones:",
        len(datos)
    )

    print(
        "TRAIN:",
        (datos["tipo"] == "TRAIN").sum()
    )

    print(
        "TEST:",
        (datos["tipo"] == "TEST").sum()
    )

    # =====================================
    # GRÁFICOS SEMANALES
    # =====================================

    semanas = (
        datos["semana_inicio"]
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    print(
        "Semanas a visualizar:",
        len(semanas)
    )

    for semana_inicio in semanas:

        semana_fin = (
            semana_inicio
            + pd.Timedelta(days=6)
        )

        datos_semana = datos[
            datos["semana_inicio"]
            == semana_inicio
        ].copy()

        if datos_semana.empty:

            continue

        # =================================
        # FIGURA
        # =================================

        plt.figure(
            figsize=(18, 6)
        )

        # =================================
        # ZONAS TRAIN / TEST
        # =================================

        train_semana = datos_semana[
            datos_semana["tipo"] == "TRAIN"
        ]

        test_semana = datos_semana[
            datos_semana["tipo"] == "TEST"
        ]

        # ---------------------------------
        # DETECTAR BLOQUES
        # ---------------------------------

        def pintar_bloques(
            datos_tipo,
            color,
            alpha,
            etiqueta
        ):

            if datos_tipo.empty:
                return

            fechas = (
                datos_tipo["datetime"]
                .sort_values()
                .tolist()
            )

            inicio_bloque = fechas[0]
            anterior = fechas[0]

            primera = True

            for fecha in fechas[1:]:

                diferencia = (
                    fecha - anterior
                )

                if diferencia > pd.Timedelta(days=1):

                    plt.axvspan(
                        inicio_bloque,
                        anterior
                        + pd.Timedelta(hours=1),
                        alpha=alpha,
                        color=color,
                        label=(
                            etiqueta
                            if primera
                            else None
                        )
                    )

                    primera = False

                    inicio_bloque = fecha

                anterior = fecha

            plt.axvspan(
                inicio_bloque,
                anterior
                + pd.Timedelta(hours=1),
                alpha=alpha,
                color=color,
                label=(
                    etiqueta
                    if primera
                    else None
                )
            )

        pintar_bloques(
            train_semana,
            "green",
            0.08,
            "TRAIN"
        )

        pintar_bloques(
            test_semana,
            "red",
            0.10,
            "TEST"
        )

        # =================================
        # VENTAS REALES
        # =================================

        plt.plot(
            datos_semana["datetime"],
            datos_semana["ventas"],
            color="black",
            linewidth=2,
            label="Ventas reales"
        )

        # =================================
        # PREDICCIONES
        # =================================

        for nombre in nombres:

            pred_df = predicciones[nombre]

            pred_semana = pred_df[
                (
                    pred_df["datetime"]
                    >= datos_semana["datetime"].min()
                )
                &
                (
                    pred_df["datetime"]
                    <= datos_semana["datetime"].max()
                )
            ]

            if pred_semana.empty:

                continue

            # ---------------------------------
            # SEPARAR TRAIN / TEST
            # ---------------------------------

            pred_train_semana = pred_semana[
                pred_semana["tipo"] == "TRAIN"
            ]

            pred_test_semana = pred_semana[
                pred_semana["tipo"] == "TEST"
            ]

            # ---------------------------------
            # PREDICCIÓN TRAIN
            # ---------------------------------

            if not pred_train_semana.empty:

                plt.plot(
                    pred_train_semana["datetime"],
                    pred_train_semana["prediccion"],
                    linewidth=1.5,
                    linestyle="--",
                    label=f"Pred. TRAIN - {nombre}"
                )

            # ---------------------------------
            # PREDICCIÓN TEST
            # ---------------------------------

            if not pred_test_semana.empty:

                plt.plot(
                    pred_test_semana["datetime"],
                    pred_test_semana["prediccion"],
                    linewidth=1.5,
                    label=f"Pred. TEST - {nombre}"
                )

        # =================================
        # TÍTULO
        # =================================

        semana_iso = (
            semana_inicio.isocalendar().week
        )

        año = semana_inicio.year

        plt.title(
            f"Semana {semana_iso} - {año} | "
            f"{semana_inicio:%d/%m/%Y} → "
            f"{semana_fin:%d/%m/%Y}"
        )

        plt.xlabel(
            "Fecha y hora"
        )

        plt.ylabel(
            "Ventas"
        )

        plt.grid(
            True,
            alpha=0.25
        )

        plt.legend()

        plt.tight_layout()

        plt.show()