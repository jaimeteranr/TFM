"""
Script principal para el entrenamiento, evaluación y comparación de los
modelos de predicción de ventas.

Coordina la carga de los datos, la construcción del conjunto de entrenamiento
y la ejecución de los distintos modelos de Machine Learning, incluyendo su
evaluación, análisis de resultados, optimización de hiperparámetros y
validación mediante la estrategia Walk-Forward.
"""

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


modelo = DecisionTreeModel(
    dataset
)

modelo.entrenar()

modelo.predecir()

modelo.evaluar()

modelo.importancia_variables()

modelo.mostrar_predicciones()

modelo.dibujar_arbol()

print("\n========================")
print("RANDOM FOREST")
print("========================")

modelo = RandomForestModel(dataset)

modelo.entrenar()

modelo.predecir()

modelo.evaluar()

modelo.importancia_variables()

modelo.mostrar_predicciones()

print("\n========================")
print("OPTIMIZACIÓN RANDOM FOREST")
print("========================")

optimizer = RandomForestOptimizer(

    modelo.X_train,
    modelo.y_train,

    modelo.X_test,
    modelo.y_test

)

resultados = optimizer.optimizar()

print("\n========================")
print("XGBOOST")
print("========================")

modelo = XGBoostModel(dataset)

modelo.entrenar()

modelo.predecir()

modelo.evaluar()

modelo.importancia_variables()

modelo.mostrar_predicciones()


print("========================")
print("WALK FORWARD - XGBOOST")
print("========================")

walk = WalkForwardValidator(

    dataset,

    XGBoostModel,

    modelo.FEATURES

)

walk.validar()

walk.resumen()

print("\n========================")
print("LSTM")
print("========================")

modelo = LSTMModel(dataset)

modelo.entrenar()

modelo.predecir()

modelo.evaluar()

modelo.importancia_variables()

modelo.mostrar_predicciones()