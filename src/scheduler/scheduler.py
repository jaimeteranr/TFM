import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).parent
    )
)

from config import *

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.append(
    str(ROOT / "utils")
)

from mod_config import *
from mod_temporada import *
from mod_demanda import *
from mod_patrones import *
from mod_cobertura import *
from mod_trabajadores import *
from mod_solver import (
    resolver_scheduler
)
from mod_solver_libre import (
    resolver_scheduler_libre
)
from mod_turnos_bloqueados import *
from mod_horarios_base import *
from mod_turnos_libres import *
from mod_cobertura_turnos import *

# =====================================
# CABECERA
# =====================================

print("\n========================")
print("VACANZE ROMANE")
print("========================")

print(
    "\nSemana:",
    FECHA_INICIO_SEMANA
)

# =====================================
# REGLAS
# =====================================

reglas = cargar_reglas()

if MODO_DEBUG:

    mostrar_reglas(
        reglas
    )

# =====================================
# TEMPORADA
# =====================================

temporada = obtener_temporada(
    FECHA_INICIO_SEMANA
)

horarios_base = (
    cargar_horarios_base(
        temporada
    )
)

if MODO_DEBUG:

    print("\n========================")
    print("TEMPORADA")
    print("========================\n")

    print(
        temporada
    )

# =====================================
# TURNOS LIBRES
# =====================================

print("\nHORARIOS BASE COMPLETOS\n")

for dia, info in horarios_base.items():

    print(
        dia,
        info
    )

turnos_libres = (
    generar_turnos_libres(
        horarios_base,
        reglas
    )
)

print("\n========================")
print("TURNOS LIBRES")
print("========================\n")

print(
    turnos_libres.head(20)
)

print(
    "\nTotal turnos:",
    len(turnos_libres)
)

cobertura_turnos = generar_cobertura_turnos(
    turnos_libres
)

print("\n========================")
print("COBERTURA TURNOS")
print("========================\n")

print(
    cobertura_turnos.head(30)
)

print(
    "\nTotal registros:",
    len(cobertura_turnos)
)

# =====================================
# DEMANDA
# =====================================

demanda = extraer_demanda(
    temporada
)

print("\n========================")
print("DEMANDA")
print("========================\n")

print(
    demanda.head(30)
)

print(
    "\nTotal registros:",
    len(demanda)
)

print("\n========================")
print("DIAS DEMANDA")
print("========================\n")

print(
    sorted(
        demanda["dia_semana"]
        .unique()
        .tolist()
    )
)

print("\n========================")
print("DIAS COBERTURA")
print("========================\n")

print(
    sorted(
        cobertura_turnos["dia"]
        .unique()
        .tolist()
    )
)

# =====================================
# PATRONES HISTORICOS
# =====================================

patrones_historicos = (
    extraer_patrones_historicos()
)

if MODO_DEBUG:

    print("\n========================")
    print("PATRONES HISTORICOS")
    print("========================\n")

    print(
        patrones_historicos.head(20)
    )

    print(
        "\nTotal patrones históricos:",
        len(patrones_historicos)
    )

# =====================================
# CATALOGO PATRONES
# =====================================

patrones = filtrar_patrones(
    patrones_historicos,
    reglas
)

if MODO_DEBUG:

    print("\n========================")
    print("CATALOGO PATRONES")
    print("========================\n")

    print(
        patrones.head(20)
    )

    print(
        "\nTotal patrones:",
        len(patrones)
    )

# =====================================
# COBERTURA PATRONES
# =====================================

cobertura_patrones = (
    generar_cobertura_patrones(
        patrones
    )
)

if MODO_DEBUG:

    print("\n========================")
    print("COBERTURA PATRONES")
    print("========================\n")

    print(
        cobertura_patrones.head(20)
    )

    print(
        "\nTotal registros:",
        len(cobertura_patrones)
    )

    print(
        "Patrones distintos:",
        cobertura_patrones[
            "patron_id"
        ].nunique()
    )

    print(
        "\nHoras cubiertas:"
    )

    print(
        sorted(
            cobertura_patrones[
                "hora"
            ].unique()
        )
    )

# =====================================
# TRABAJADORES ACTIVOS
# =====================================

activos = (
    obtener_trabajadores_activos(
        FECHA_INICIO_SEMANA
    )
)

print(
    "\nModo trabajadores:",
    (
        "FECHAS"
        if USAR_FECHA_BAJA
        else
        "ACTIVO"
    )
)

turnos_bloqueados = (
    cargar_turnos_bloqueados()
)

print("\nTURNOS BLOQUEADOS\n")
print(turnos_bloqueados)

# =====================================
# CAPACIDAD SEMANAL
# =====================================

horas_bloqueadas = 0

if len(turnos_bloqueados) > 0:

    horas_bloqueadas = (

        turnos_bloqueados[
            "duracion"
        ].sum()

    )

horas_disponibles = (

    len(activos)

    *

    reglas["horas_semanales"]

    +

    horas_bloqueadas

)

horas_demandadas = (
    demanda["demanda"].sum()
    * 0.5
)

if horas_disponibles < horas_demandadas:

    modo_planificacion = "DEFICIT"

else:

    modo_planificacion = "EXCESO"

print("\n========================")
print("CAPACIDAD")
print("========================\n")

print(
    f"Horas disponibles: {horas_disponibles}"
)

print(
    f"Horas demandadas: {horas_demandadas}"
)

print(
    f"Modo: {modo_planificacion}"
)

print(
    "Descansos:",
    ACTIVAR_DESCANSOS
)

if MODO_DEBUG:

    print("\n========================")
    print("TRABAJADORES ACTIVOS")
    print("========================\n")

    print(
        activos[
            [
                "id",
                "nombre"
            ]
        ]
    )

    print(
        "\nTotal activos:",
        len(activos)
    )

# =====================================
# SOLVER
# =====================================

if MODO_SOLVER == "PATRONES":


    print("\nSOLVER: PATRONES")

    calendario = resolver_scheduler(
        activos,
        demanda,
        patrones,
        cobertura_patrones,
        reglas,
        modo_planificacion,
        turnos_bloqueados,
        horarios_base,
        temporada
    )

elif MODO_SOLVER == "LIBRE":

    print("\nSOLVER: LIBRE")

    calendario = resolver_scheduler_libre(
        activos,
        demanda,
        turnos_libres,
        cobertura_turnos,
        reglas,
        modo_planificacion,
        turnos_bloqueados,
        horarios_base,
        temporada
    )

else:

    raise ValueError(
        f"MODO_SOLVER desconocido: {MODO_SOLVER}"
    )

if calendario is not None:

    if MOSTRAR_CALENDARIO:

        print("\n========================")
        print("CALENDARIO")
        print("========================\n")

        print(
            calendario
        )

    calendario.to_excel(
        "data/outputs/calendario_generado.xlsx",
        index=False
    )

    print(
        "\nGuardado data/outputs/calendario_generado.xlsx"
    )

# =====================================
# VISUALIZACION
# =====================================

from mod_visualizacion import *

generar_visualizacion()