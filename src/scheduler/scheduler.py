import sys
from pathlib import Path


sys.path.append(
    str(
        Path(__file__).parent
    )
)

from variables_entrada import *
ROOT = Path(__file__).resolve().parent.parent

sys.path.append(
    str(ROOT / "utils")
)

from mod_config import SchedulerConfig
from mod_temporada import Temporada
from mod_demanda import DemandaExtractor
from mod_patrones import PatronesManager
from mod_cobertura import CoberturaPatronesGenerator
from mod_trabajadores import Trabajadores
from mod_solver import SolverPatrones
from mod_solver_libre import SolverLibre
from mod_turnos_bloqueados import TurnosBloqueados
from mod_horarios_base import HorariosBaseLoader
from mod_turnos_libres import TurnosLibres
from mod_cobertura_turnos import CoberturaTurnosGenerator

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
config = SchedulerConfig()

reglas = config.cargar()

if MODO_DEBUG:

    config.mostrar()

# =====================================
# TEMPORADA
# =====================================

temporada = Temporada().obtener_temporada(
    FECHA_INICIO_SEMANA
)

loader_horarios = HorariosBaseLoader()

horarios_base = loader_horarios.cargar(
    temporada
)

if MODO_DEBUG:

    print("\n========================")
    print("TEMPORADA")
    print("========================\n")

    print(
        temporada
    )

if MODO_DEBUG:
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
    TurnosLibres().generar_turnos_libres(
        horarios_base,
        reglas
    )
)

if MODO_DEBUG:

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

cobertura_turnos_generator = CoberturaTurnosGenerator(
    turnos_libres
)

cobertura_turnos = (
    cobertura_turnos_generator.generar()
)

if MODO_DEBUG: 
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

extractor_demanda = DemandaExtractor()

if MODO_DEMANDA == "HISTORICA":

    demanda = extractor_demanda.extraer_historica(
        temporada
    )

elif MODO_DEMANDA == "PREDICCION":

    demanda = extractor_demanda.extraer_prediccion(
        FECHA_INICIO_SEMANA
    )

else:

    raise ValueError(
        f"MODO_DEMANDA desconocido: {MODO_DEMANDA}"
    )

if MODO_DEBUG: 

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

patrones_manager = PatronesManager()

patrones_historicos = (
    patrones_manager.extraer_historicos()
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

patrones = patrones_manager.filtrar(
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

cobertura_patrones_generator = CoberturaPatronesGenerator(
    patrones
)

cobertura_patrones = (
    cobertura_patrones_generator.generar()
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
    Trabajadores().obtener_trabajadores_activos(
        FECHA_INICIO_SEMANA
    )
)

if MODO_DEBUG: 

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
    TurnosBloqueados().cargar_turnos_bloqueados()
)

if MODO_DEBUG: 

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

if MODO_DEBUG: 
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

    solver = SolverPatrones()

    calendario = solver.resolver(
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

    # if MODO_DEBUG:
        
        # print("\nTURNOS LIBRES")
        # print(turnos_libres.head())
        # print(turnos_libres.columns)

        # print("\nCOBERTURA TURNOS")
        # print(cobertura_turnos.head())
        # print(cobertura_turnos.columns)

    turnos_libres = turnos_libres.rename(
        columns={
            "turno_id": "patron_id",
            "entrada": "entrada_norm",
            "duracion": "duracion_norm",
        }
    )

    cobertura_turnos = cobertura_turnos.rename(
        columns={
            "turno_id": "patron_id"
        }
    )

    solver = SolverLibre()

    calendario = solver.resolver(
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

from mod_visualizacion import Visualizacion

Visualizacion().generar_visualizacion()