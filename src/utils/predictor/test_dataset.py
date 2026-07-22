"""
Script de prueba para la construcción y validación del dataset diario.

Ejecuta el flujo completo de carga de datos, generación del conjunto de
entrenamiento y análisis exploratorio del resultado, permitiendo comprobar
el correcto funcionamiento de los distintos módulos implicados en la
preparación del dataset.
"""

import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent
    )
)

ROOT = Path(__file__).resolve().parent.parent

sys.path.append(
    str(ROOT / "predictor")
)

from mod_cargar_ventas import VentasLoader
from mod_cargar_meteorologia import MeteorologiaLoader
from mod_dataset import DatasetBuilder
from mod_analisis_dataset import DatasetAnalyzer
from mod_analisis import DatasetVisualizer
from mod_cargar_eventos import EventosLoader

print("\n========================")
print("VENTAS")
print("========================")

ventas = VentasLoader().cargar()


print(ventas.head())

print()

print(ventas.tail())

print()

print(ventas.info())

print("\n========================")
print("METEOROLOGÍA")
print("========================")

meteorologia_loader = MeteorologiaLoader()
meteorologia, meteorologia_diaria = meteorologia_loader.cargar()

print(meteorologia_diaria.head())

print()

print(meteorologia_diaria.info())

print("\n========================")
print("EVENTOS")
print("========================")

eventos_loader = EventosLoader()
eventos = eventos_loader.cargar()

print(eventos.head())

print()

print(eventos.info())

dataset_builder = DatasetBuilder(

    ventas,
    meteorologia_diaria,
    eventos

)

dataset = dataset_builder.crear()

print("\n========================")
print("DATASET")
print("========================")

print(dataset.head())

print()

print(dataset.info())

print("\n========================")
print("ANÁLISIS DATASET")
print("========================")

dataset_analyzer = DatasetAnalyzer(
    dataset
)

dataset_analyzer.analizar()

visualizer = DatasetVisualizer(
    dataset
)

visualizer.visualizar()

