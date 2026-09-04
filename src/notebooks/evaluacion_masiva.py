import pandas as pd

from src.scheduler.scheduler import generar_calendario


# ============================================
# CARGAR PLANTILLA SEMANAL
# ============================================

plantilla_semanal = pd.read_excel(
    "data/outputs/plantilla_semanal.xlsx"
)

plantilla_semanal["inicio_semana"] = pd.to_datetime(
    plantilla_semanal["inicio_semana"]
)


# ============================================
# SEMANAS A GENERAR
# ============================================

semanas = plantilla_semanal


resultados = []


# ============================================
# GENERACIÓN DE CALENDARIOS
# ============================================

for numero_semana, (_, semana) in enumerate(
    semanas.iterrows(),
    start=1
):

    fecha = semana["inicio_semana"]

    numero_trabajadores = int(
        semana["numero_trabajadores"]
    )

    print("\n================================")
    print(
        f"GENERANDO SEMANA {numero_semana}/{len(semanas)}"
    )
    print("================================")

    print(
        "Semana:",
        fecha.strftime("%Y-%m-%d")
    )

    print(
        "Trabajadores:",
        numero_trabajadores
    )

    calendario = generar_calendario(
        fecha_inicio_semana=fecha,
        numero_trabajadores=numero_trabajadores
    )

    if calendario is None:

        print(
            "⚠️ No se obtuvo solución."
        )

        continue

    calendario = calendario.copy()

    calendario["inicio_semana"] = fecha

    calendario["numero_trabajadores"] = (
        numero_trabajadores
    )

    resultados.append(
        calendario
    )

    print(
        "✓ Calendario generado"
    )


# ============================================
# UNIR RESULTADOS
# ============================================

if resultados:

    calendarios = pd.concat(
        resultados,
        ignore_index=True
    )

    print("\n================================")
    print("RESULTADO FINAL")
    print("================================")

    print(
        "Semanas generadas:",
        len(resultados),
        "/",
        len(semanas)
    )

    print(
        "Registros:",
        len(calendarios)
    )

    # ========================================
    # GUARDAR
    # ========================================

    calendarios.to_excel(
        "data/outputs/calendarios_evaluacion_masiva.xlsx",
        index=False
    )

    print(
        "\nGuardado:"
        " data/outputs/calendarios_evaluacion_masiva.xlsx"
    )

else:

    print(
        "No se generó ningún calendario."
    )