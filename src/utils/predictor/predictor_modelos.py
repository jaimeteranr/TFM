"""
Script principal para el entrenamiento, evaluación y comparación de los
modelos de predicción de ventas.

Coordina la carga de los datos, la construcción del conjunto de entrenamiento
y la ejecución de los distintos modelos de Machine Learning, incluyendo su
evaluación, análisis de resultados, optimización de hiperparámetros y
validación mediante la estrategia Walk-Forward.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

sys.path.append(
    str(ROOT / "scheduler")
)

from variables_entrada import TIPO_PREDICCION

from mod_cargar_ventas_horario import VentasLoader
from mod_cargar_meteorologia import MeteorologiaLoader
from mod_cargar_eventos import EventosLoader
from mod_dataset_horario import DatasetBuilder

from models.mod_decision_tree import DecisionTreeModel
from models.mod_random_forest import RandomForestModel
from models.mod_random_forest_optimizer import RandomForestOptimizer
from models.mod_xgboost import XGBoostModel
from models.mod_walk_forward import WalkForwardValidator
from models.mod_lstm import LSTMModel
from pathlib import Path

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from models.mod_visualizacion_modelos import (
    comparar_modelos,
    comparar_modelos_train
)

MODELS_PATH = (
    Path(__file__).resolve().parent / "models"
)

MODELS_COMPLETA = (
    MODELS_PATH / "completa"
)

MODELS_VERANO = (
    MODELS_PATH / "estacional" / "verano"
)

MODELS_INVIERNO = (
    MODELS_PATH / "estacional" / "invierno"
)

def calcular_metricas(modelo):

    y_real = np.asarray(
        modelo.y_test
    ).ravel()

    pred = np.asarray(
        modelo.predicciones
    ).ravel()

    mae = mean_absolute_error(
        y_real,
        pred
    )

    mse = mean_squared_error(
        y_real,
        pred
    )

    rmse = mse ** 0.5

    r2 = r2_score(
        y_real,
        pred
    )

    return {
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2
    }

def evaluar_un_modelo(
    modelo,
    nombre
):

    print()
    print("========================")
    print(f"EVALUACIÓN - {nombre}")
    print("========================")

    # =====================================
    # MÉTRICAS
    # =====================================

    metricas = calcular_metricas(
        modelo
    )

    print()
    print("RESULTADOS")
    print("------------------------")

    print(
        f"MAE : {metricas['MAE']:.2f}"
    )

    print(
        f"RMSE: {metricas['RMSE']:.2f}"
    )

    print(
        f"R²  : {metricas['R2']:.4f}"
    )

    # =====================================
    # IMPORTANCIA DE VARIABLES
    # =====================================

    print()
    print("========================")
    print("IMPORTANCIA VARIABLES")
    print("========================")

    try:
        modelo.importancia_variables()
    except AttributeError:
        print(
            "Este modelo no dispone de importancia de variables."
        )

    # =====================================
    # PREDICCIONES
    # =====================================

    print()
    print("========================")
    print("PREDICCIONES")
    print("========================")

    try:
        modelo.mostrar_predicciones()
    except AttributeError:
        print(
            "Este modelo no dispone de mostrar_predicciones()."
        )

    return metricas

def ejecutar_modelo(
    modelo_clase,
    dataset,
    ruta_verano=None,
    ruta_invierno=None,
    ruta_completa=None
):

    # =====================================
    # COMPLETA
    # =====================================

    if TIPO_PREDICCION == "completa":

        if modelo_clase in (
            XGBoostModel,
            LSTMModel
        ):

            modelo = modelo_clase(
                dataset,
                ruta_modelo=ruta_completa
            )

        else:

            modelo = modelo_clase(
                dataset
            )

        modelo.medir_entrenamiento()

        modelo.medir_prediccion()

        return modelo


    # =====================================
    # ESTACIONAL
    # =====================================

    elif TIPO_PREDICCION == "estacional":

        dataset_verano, dataset_invierno = (
            separar_estaciones(dataset)
        )

        # -------------------------
        # VERANO
        # -------------------------

        if modelo_clase in (
            XGBoostModel,
            LSTMModel
        ):

            modelo_verano = modelo_clase(
                dataset_verano,
                ruta_modelo=ruta_verano
            )

        else:

            modelo_verano = modelo_clase(
                dataset_verano
            )

        modelo_verano.medir_entrenamiento()

        modelo_verano.medir_prediccion()

        # -------------------------
        # INVIERNO
        # -------------------------

        if modelo_clase in (
            XGBoostModel,
            LSTMModel
        ):

            modelo_invierno = modelo_clase(
                dataset_invierno,
                ruta_modelo=ruta_invierno
            )

        else:

            modelo_invierno = modelo_clase(
                dataset_invierno
            )

        modelo_invierno.medir_entrenamiento()

        modelo_invierno.medir_prediccion()

        return (
            modelo_verano,
            modelo_invierno
        )


    # =====================================
    # MENSUAL
    # =====================================

    elif TIPO_PREDICCION == "mensual":

        datasets_meses = separar_meses(
            dataset
        )

        modelos = {}

        nombres_meses = {
            1: "ENERO",
            2: "FEBRERO",
            3: "MARZO",
            4: "ABRIL",
            5: "MAYO",
            6: "JUNIO",
            7: "JULIO",
            8: "AGOSTO",
            9: "SEPTIEMBRE",
            10: "OCTUBRE",
            11: "NOVIEMBRE",
            12: "DICIEMBRE"
        }

        for mes in range(1, 13):

            print()
            print("========================")
            print(
                f"{nombres_meses[mes]}"
            )
            print("========================")

            dataset_mes = datasets_meses[mes]

            if dataset_mes.empty:

                print(
                    f"No hay datos para {nombres_meses[mes]}"
                )

                continue

            # =================================
            # RUTA DEL MES
            # =================================

            ruta_mes = (
                MODELS_PATH
                / "mensual"
                / nombres_meses[mes].lower()
            )

            ruta_mes.mkdir(
                parents=True,
                exist_ok=True
            )

            # =================================
            # CREAR MODELO
            # =================================

            if modelo_clase in (
                XGBoostModel,
                LSTMModel
            ):

                modelo = modelo_clase(
                    dataset_mes,
                    ruta_modelo=ruta_mes
                )

            else:

                modelo = modelo_clase(
                    dataset_mes
                )

            # =================================
            # ENTRENAR
            # =================================

            modelo.medir_entrenamiento()

            modelo.medir_prediccion()

            modelos[mes] = modelo

        return modelos


    else:

        raise ValueError(
            f"TIPO_PREDICCION desconocido: "
            f"{TIPO_PREDICCION}"
        )

def evaluar_modelo(
    resultado,
    nombre
):

    # =====================================
    # COMPLETA
    # =====================================

    if TIPO_PREDICCION == "completa":

        modelo = resultado

        evaluar_un_modelo(
            modelo,
            nombre
        )

        return


    # =====================================
    # ESTACIONAL
    # =====================================

    elif TIPO_PREDICCION == "estacional":

        modelo_verano, modelo_invierno = resultado

        resultados = []

        for modelo, temporada in [
            (modelo_verano, "VERANO"),
            (modelo_invierno, "INVIERNO")
        ]:

            metricas = calcular_metricas(
                modelo
            )

            resultados.append(
                metricas
            )

            print(
                f"{nombre} - {temporada}"
            )

            print(metricas)

                # MEDIA

            tabla = pd.DataFrame(resultados)

            print()
            print("------------------------")
            print("MEDIA ESTACIONAL")
            print("------------------------")

            print(
                tabla[
                    [
                        "MAE",
                        "RMSE",
                        "R2"
                    ]
                ].mean()
            )

            return


    # =====================================
    # MENSUAL
    # =====================================

    elif TIPO_PREDICCION == "mensual":

        nombres_meses = {
            1: "ENERO",
            2: "FEBRERO",
            3: "MARZO",
            4: "ABRIL",
            5: "MAYO",
            6: "JUNIO",
            7: "JULIO",
            8: "AGOSTO",
            9: "SEPTIEMBRE",
            10: "OCTUBRE",
            11: "NOVIEMBRE",
            12: "DICIEMBRE"
        }

        resultados = []

        print()
        print("========================")
        print(
            f"EVALUACIÓN MENSUAL - {nombre}"
        )
        print("========================")

        for mes, modelo in resultado.items():

            metricas = calcular_metricas(
                modelo
            )

            metricas["Mes"] = nombres_meses[mes]

            resultados.append(
                metricas
            )

        tabla = pd.DataFrame(
            resultados
        )

        print()
        print(tabla)

        # =================================
        # MEDIA
        # =================================

        print()
        print("------------------------")
        print("MEDIA")
        print("------------------------")

        print(
            tabla[
                [
                    "MAE",
                    "RMSE",
                    "R2"
                ]
            ].mean()
        )

        return

print("\n========================")
print("DECISION TREE")
print("========================")

ventas = VentasLoader().cargar()

meteorologia_loader = MeteorologiaLoader()

meteorologia, _ = meteorologia_loader.cargar()

eventos = EventosLoader().cargar()

dataset = DatasetBuilder(

    ventas,

    meteorologia,

    eventos

).crear()

# =====================================
# DATASETS ESTACIONALES
# =====================================

def separar_estaciones(dataset):

    dataset = dataset.copy()

    fecha = dataset["Fecha"]

    # -------------------------
    # VERANO
    # 15 junio -> 15 septiembre
    # -------------------------

    verano = (
        (
            (fecha.dt.month > 6)
            |
            (
                (fecha.dt.month == 6)
                & (fecha.dt.day >= 15)
            )
        )
        &
        (
            (fecha.dt.month < 9)
            |
            (
                (fecha.dt.month == 9)
                & (fecha.dt.day <= 15)
            )
        )
    )

    # -------------------------
    # INVIERNO
    # 16 septiembre -> 14 junio
    # -------------------------

    invierno = ~verano

    dataset_verano = dataset[
        verano
    ].copy()

    dataset_invierno = dataset[
        invierno
    ].copy()

    return (
        dataset_verano,
        dataset_invierno
    )

def separar_meses(dataset):

    meses = {}

    for mes in range(1, 13):

        meses[mes] = dataset[
            dataset["Fecha"].dt.month == mes
        ].copy()

    return meses


modelo_dt = ejecutar_modelo(
    DecisionTreeModel,
    dataset
)

evaluar_modelo(
    modelo_dt,
    "DECISION TREE"
)

print("\n========================")
print("RANDOM FOREST")
print("========================")

modelo_rf = ejecutar_modelo(
    RandomForestModel,
    dataset
)

evaluar_modelo(
    modelo_rf,
    "RANDOM FOREST"
)

print("\n========================")
print("OPTIMIZACIÓN RANDOM FOREST")
print("========================")

if TIPO_PREDICCION != "mensual":

    if TIPO_PREDICCION == "completa":

        modelo_rf_opt = modelo_rf

    elif TIPO_PREDICCION == "estacional":

        # De momento optimizamos utilizando
        # el modelo de verano como referencia

        modelo_rf_opt = modelo_rf[0]

    optimizer = RandomForestOptimizer(

        modelo_rf_opt.X_train,
        modelo_rf_opt.y_train,

        modelo_rf_opt.X_test,
        modelo_rf_opt.y_test

    )

    resultados = optimizer.optimizar()

print("\n========================")
print("XGBOOST")
print("========================")

modelo_xgb = ejecutar_modelo(
    XGBoostModel,
    dataset,
    ruta_verano=MODELS_VERANO,
    ruta_invierno=MODELS_INVIERNO,
    ruta_completa=MODELS_COMPLETA
)

evaluar_modelo(
    modelo_xgb,
    "XGBOOST"
)


print("========================")
print("WALK FORWARD - XGBOOST")
print("========================")

walk = WalkForwardValidator(

    dataset,

    XGBoostModel,

    XGBoostModel.FEATURES

)

walk.validar()

walk.resumen()

print("\n========================")
print("LSTM")
print("========================")

# =====================================
# LSTM
# =====================================

if TIPO_PREDICCION == "completa":

    modelo_lstm = ejecutar_modelo(
        LSTMModel,
        dataset,
        ruta_verano=MODELS_VERANO,
        ruta_invierno=MODELS_INVIERNO,
        ruta_completa=MODELS_COMPLETA
    )

    modelos_lstm_evaluar = [
        ("LSTM", modelo_lstm)
    ]


elif TIPO_PREDICCION == "estacional":

    modelo_lstm = ejecutar_modelo(
        LSTMModel,
        dataset,
        ruta_verano=MODELS_VERANO,
        ruta_invierno=MODELS_INVIERNO,
        ruta_completa=MODELS_COMPLETA
    )

    modelos_lstm_evaluar = [
        ("LSTM VERANO", modelo_lstm[0]),
        ("LSTM INVIERNO", modelo_lstm[1])
    ]


elif TIPO_PREDICCION == "mensual":

    modelo_lstm = ejecutar_modelo(
        LSTMModel,
        dataset,
        ruta_verano=MODELS_VERANO,
        ruta_invierno=MODELS_INVIERNO,
        ruta_completa=MODELS_COMPLETA
    )

    modelos_lstm_evaluar = []

    nombres_meses = {
        1: "ENERO",
        2: "FEBRERO",
        3: "MARZO",
        4: "ABRIL",
        5: "MAYO",
        6: "JUNIO",
        7: "JULIO",
        8: "AGOSTO",
        9: "SEPTIEMBRE",
        10: "OCTUBRE",
        11: "NOVIEMBRE",
        12: "DICIEMBRE"
    }

    for mes, modelo in modelo_lstm.items():

        modelos_lstm_evaluar.append(
            (
                f"LSTM {nombres_meses[mes]}",
                modelo
            )
        )

# =====================================
# EVALUACIÓN LSTM
# =====================================

for nombre, modelo in modelos_lstm_evaluar:

    print()
    print("========================")
    print(nombre)
    print("========================")

    print(
        "Test:",
        modelo.test.shape
    )

    print(
        "X_test:",
        modelo.X_test.shape
    )

    print(
        "y_test:",
        modelo.y_test.shape
    )

    # ---------------------------------
    # VENTANA DE EJEMPLO
    # ---------------------------------

    if len(modelo.test) >= 24:

        ventana = modelo.test.iloc[:24].copy()

        X = modelo.crear_secuencia(
            ventana
        )

        print(
            "Ventana:",
            X.shape
        )

        pred = modelo.model.predict(
            X,
            verbose=0
        )

        pred = modelo.scaler_y.inverse_transform(
            pred
        )

        print(
            "Predicción:",
            pred
        )

    # ---------------------------------
    # EVALUACIÓN
    # ---------------------------------

    modelo.evaluar()

    modelo.importancia_variables()

    modelo.mostrar_predicciones()

# =====================================
# COMPARACIÓN DE MODELOS
# =====================================

if TIPO_PREDICCION == "completa":

    comparar_modelos(
        [
            modelo_dt,
            modelo_rf,
            modelo_xgb,
            modelo_lstm
        ],
        nombres=[
            "Decision Tree",
            "Random Forest",
            "XGBoost",
            "LSTM"
        ],
        n=250
    )


elif TIPO_PREDICCION == "estacional":

    print()
    print("========================")
    print("COMPARACIÓN - VERANO")
    print("========================")

    comparar_modelos(
        [
            modelo_dt[0],
            modelo_rf[0],
            modelo_xgb[0],
            modelo_lstm[0]
        ],
        nombres=[
            "Decision Tree",
            "Random Forest",
            "XGBoost",
            "LSTM"
        ],
        n=250
    )

    print()
    print("========================")
    print("COMPARACIÓN - INVIERNO")
    print("========================")

    comparar_modelos(
        [
            modelo_dt[1],
            modelo_rf[1],
            modelo_xgb[1],
            modelo_lstm[1]
        ],
        nombres=[
            "Decision Tree",
            "Random Forest",
            "XGBoost",
            "LSTM"
        ],
        n=250
    )


elif TIPO_PREDICCION == "mensual":

    nombres_meses = {
        1: "ENERO",
        2: "FEBRERO",
        3: "MARZO",
        4: "ABRIL",
        5: "MAYO",
        6: "JUNIO",
        7: "JULIO",
        8: "AGOSTO",
        9: "SEPTIEMBRE",
        10: "OCTUBRE",
        11: "NOVIEMBRE",
        12: "DICIEMBRE"
    }

    for mes in range(1, 13):

        print()
        print("========================")
        print(
            f"COMPARACIÓN - {nombres_meses[mes]}"
        )
        print("========================")

        comparar_modelos(
            [
                modelo_dt[mes],
                modelo_rf[mes],
                modelo_xgb[mes],
                modelo_lstm[mes]
            ],
            nombres=[
                "Decision Tree",
                "Random Forest",
                "XGBoost",
                "LSTM"
            ],
            n=250
        )