"""
Módulo encargado de resolver el problema de planificación de calendarios de
trabajo a partir de un catálogo de patrones de turno.

Implementa el modelo de optimización utilizado para asignar turnos al
personal, integrando la demanda prevista, las restricciones operativas y las
reglas de planificación con el objetivo de generar un calendario de trabajo
factible y optimizado.
"""

from ortools.sat.python import cp_model
import pandas as pd

from variables_entrada import *
from solution_printer import SolutionPrinter


class SolverPatrones:
    """
    Resuelve el problema de asignación de turnos mediante optimización.

    Construye y ejecuta el modelo de planificación a partir de la información
    disponible sobre trabajadores, patrones de turno, demanda y reglas del
    sistema, obteniendo un calendario de trabajo que satisface las
    restricciones definidas y optimiza los criterios establecidos para la
    planificación.
    """

    def resolver(
        self,
        activos,
        demanda,
        patrones,
        cobertura_patrones,
        reglas,
        modo_planificacion,
        turnos_bloqueados,
        horarios_base,
        temporada
    ):

        # =====================================
        # DIAS
        # =====================================

        dias = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]

        trabajadores_apertura = activos[
            activos["apertura"] == 1
        ]["id"].tolist()

        trabajadores_cierre = activos[
            activos["cierre"] == 1
        ]["id"].tolist()

        # =====================================
        # REGLAS
        # =====================================

        horas_semanales = int(
            reglas["horas_semanales"]
        )

        max_dias_semana = int(
            reglas["max_dias_semana"]
        )

        descanso_entre_turnos = int(
            reglas["descanso_entre_turnos"]
        )

        trabajadores_apertura = activos[
            activos["apertura"] == 1
        ]["id"].tolist()

        trabajadores_cierre = activos[
            activos["cierre"] == 1
        ]["id"].tolist()

        min_personas_cierre = int(
            reglas["min_personas_cierre"]
        )




        # OR-Tools trabaja en bloques de 30 min

        horas_objetivo = (
            horas_semanales * 2
        )

        # =====================================
        # PATRON -> HORAS
        # =====================================

        patron_horas = {}

        for patron_id in patrones["patron_id"]:

            patron_horas[patron_id] = list(

                cobertura_patrones[
                    cobertura_patrones["patron_id"]
                    == patron_id
                ]["hora"]

            )

        # =====================================
        # COBERTURA BLOQUEADA
        # =====================================

        cobertura_bloqueada = {}

        if len(turnos_bloqueados) > 0:

            for _, fila in turnos_bloqueados.iterrows():

                dia = fila["dia"]

                entrada = str(
                    fila["entrada"]
                )[:5]

                entrada = pd.to_datetime(
                    entrada,
                    format="%H:%M"
                )

                duracion = float(
                    fila["duracion"]
                )

                bloques = int(
                    duracion * 2
                )

                actual = entrada

                for _ in range(bloques):

                    hora = actual.strftime(
                        "%H:%M"
                    )

                    clave = (
                        dia,
                        hora
                    )

                    cobertura_bloqueada[
                        clave
                    ] = cobertura_bloqueada.get(
                        clave,
                        0
                    ) + 1

                    actual += pd.Timedelta(
                        minutes=30
                    )

        # =====================================
        # PATRON -> HORA DESCANSO
        # =====================================

        patron_descanso = {}

        for _, fila in patrones.iterrows():

            patron_id = fila["patron_id"]

            duracion = float(
                fila["duracion_norm"]
            )

            if duracion <= 6:

                patron_descanso[
                    patron_id
                ] = None

                continue

            entrada = pd.to_datetime(
                fila["entrada_norm"],
                format="%H:%M"
            )

            # mitad redondeada hacia arriba

            horas_descanso = int(
                (duracion / 2)
                + 0.999
            )

            instante_descanso = (

                entrada

                + pd.Timedelta(
                    hours=horas_descanso
                )

            )

            patron_descanso[
                patron_id
            ] = instante_descanso.strftime(
                "%H:%M"
            )

        # =====================================
        # INICIO Y FIN DE PATRON
        # =====================================

        def obtener_inicio_fin_patron(
            entrada,
            duracion
        ):

            inicio = pd.to_datetime(
                entrada,
                format="%H:%M"
            )

            fin = inicio + pd.Timedelta(
                hours=duracion
            )

            return inicio, fin


        if MODO_DEBUG:
            print("\nDEMANDA POR DIA")
            print(
                demanda.groupby("dia_semana")["demanda"].sum()
            )

            print("\nDEMANDA VIERNES TARDE")
            print(
                demanda[
                    (demanda["dia_semana"] == "Friday")
                    &
                    (demanda["hora"] >= "00:00")
                ]
            )

            print("\nDEMANDA SABADO TARDE")
            print(
                demanda[
                    (demanda["dia_semana"] == "Saturday")
                    &
                    (demanda["hora"] >= "00:00")
                ]
            )

        # =====================================
        # MODELO
        # =====================================

        model = cp_model.CpModel()

        # =====================================
        # VARIABLES
        # =====================================

        x = {}

        for w in activos["id"]:

            for d in dias:

                for p in patrones["patron_id"]:

                    x[w, d, p] = model.NewBoolVar(
                        f"x_{w}_{d}_{p}"
                    )

        
        # =====================================
        # DIAS CERRADOS
        # =====================================

        for dia in dias:

            if not horarios_base[dia]["abierto"]:

                for w in activos["id"]:

                    for p in patrones["patron_id"]:

                        model.Add(
                            x[w, dia, p] == 0
                        )

        # # =====================================
        # # PATRONES FUERA DE HORARIO
        # # =====================================

        # for dia in dias:

        #     if not horarios_base[dia]["abierto"]:
        #         continue

        #     cierre_txt = horarios_base[dia]["cierre"]

        #     cierre = pd.to_datetime(
        #         cierre_txt,
        #         format="%H:%M"
        #     )

        #     # si el cierre es de madrugada
        #     if cierre.hour < 6:
        #         cierre += pd.Timedelta(days=1)

        #     for _, patron in patrones.iterrows():

        #         entrada = pd.to_datetime(
        #             patron["entrada_norm"],
        #             format="%H:%M"
        #         )

        #         salida = (
        #             entrada
        #             + pd.Timedelta(
        #                 hours=float(
        #                     patron["duracion_norm"]
        #                 )
        #             )
        #         )

        #         # patrón termina después del cierre
        #         if salida > cierre:

        #             for w in activos["id"]:

        #                 model.Add(
        #                     x[
        #                         w,
        #                         dia,
        #                         patron["patron_id"]
        #                     ] == 0
        #                 )

        # print("\nPATRONES ELIMINADOS POR CIERRE")

        # for dia in dias:

        #     if not horarios_base[dia]["abierto"]:
        #         continue

        #     contador = 0

        #     cierre_txt = horarios_base[dia]["cierre"]

        #     cierre = pd.to_datetime(
        #         cierre_txt,
        #         format="%H:%M"
        #     )

        #     if cierre.hour < 6:
        #         cierre += pd.Timedelta(days=1)

        #     for _, patron in patrones.iterrows():

        #         entrada = pd.to_datetime(
        #             patron["entrada_norm"],
        #             format="%H:%M"
        #         )

        #         salida = (
        #             entrada
        #             + pd.Timedelta(
        #                 hours=float(
        #                     patron["duracion_norm"]
        #                 )
        #             )
        #         )

        #         if salida > cierre:
        #             contador += 1

        #     print(dia, contador)

        # # =====================================
        # # DEBUG PATRONES FUERA DE HORARIO
        # # =====================================

        # print("\nPATRONES QUE TERMINAN DESPUES DEL CIERRE")

        # for dia in dias:

        #     if not horarios_base[dia]["abierto"]:
        #         continue

        #     cierre = horarios_base[dia]["cierre"]

        #     contador = 0

        #     for _, p in patrones.iterrows():

        #         entrada = pd.to_datetime(
        #             p["entrada_norm"],
        #             format="%H:%M"
        #         )

        #         salida = (
        #             entrada
        #             + pd.Timedelta(
        #                 hours=float(
        #                     p["duracion_norm"]
        #                 )
        #             )
        #         )

        #         salida_txt = salida.strftime("%H:%M")

        #         if cierre < "06:00":

        #             if salida_txt > cierre and salida_txt < "06:00":
        #                 contador += 1

        #         else:

        #             if salida_txt > cierre:
        #                 contador += 1

        #     print(
        #         f"{dia}: {contador}"
        #     )


        # =====================================
        # MAX 1 TURNO POR DIA
        # =====================================

        for w in activos["id"]:

            for d in dias:

                model.Add(

                    sum(
                        x[w, d, p]
                        for p in patrones["patron_id"]
                    )

                    <= 1

                )

        # =====================================
        # LIBRANZAS FIN DE SEMANA
        # =====================================

        trabajan_sabado = []
        trabajan_domingo = []

        for w in activos["id"]:

            trabaja_sabado = model.NewBoolVar(
                f"sabado_{w}"
            )

            trabaja_domingo = model.NewBoolVar(
                f"domingo_{w}"
            )

            model.Add(

                sum(
                    x[w, "Saturday", p]
                    for p in patrones["patron_id"]
                )

                >= 1

            ).OnlyEnforceIf(
                trabaja_sabado
            )

            model.Add(

                sum(
                    x[w, "Saturday", p]
                    for p in patrones["patron_id"]
                )

                == 0

            ).OnlyEnforceIf(
                trabaja_sabado.Not()
            )

            model.Add(

                sum(
                    x[w, "Sunday", p]
                    for p in patrones["patron_id"]
                )

                >= 1

            ).OnlyEnforceIf(
                trabaja_domingo
            )

            model.Add(

                sum(
                    x[w, "Sunday", p]
                    for p in patrones["patron_id"]
                )

                == 0

            ).OnlyEnforceIf(
                trabaja_domingo.Not()
            )

            trabajan_sabado.append(
                trabaja_sabado
            )

            trabajan_domingo.append(
                trabaja_domingo
            )

        if temporada.lower() == "verano":

            model.Add(
                sum(trabajan_sabado)
                == len(activos) - 1
            )

            model.Add(
                sum(trabajan_domingo)
                == len(activos) - 1
            )

        else:

            model.Add(
                sum(trabajan_sabado)
                == len(activos)
            )

            model.Add(
                sum(trabajan_domingo)
                == len(activos)
            )

        # =====================================
        # DESCANSO ENTRE TURNOS
        # =====================================

        for w in activos["id"]:

            for i in range(
                len(dias) - 1
            ):

                dia_actual = dias[i]

                dia_siguiente = dias[i + 1]

                for _, p1 in patrones.iterrows():

                    inicio1, fin1 = (
                        obtener_inicio_fin_patron(
                            p1["entrada_norm"],
                            p1["duracion_norm"]
                        )
                    )

                    for _, p2 in patrones.iterrows():

                        inicio2, _ = (
                            obtener_inicio_fin_patron(
                                p2["entrada_norm"],
                                p2["duracion_norm"]
                            )
                        )

                        inicio2 = (
                            inicio2
                            +
                            pd.Timedelta(days=1)
                        )

                        horas_descanso = (

                            inicio2
                            -
                            fin1

                        ).total_seconds() / 3600

                        if (

                            horas_descanso
                            <
                            descanso_entre_turnos

                        ):

                            model.Add(

                                x[
                                    w,
                                    dia_actual,
                                    p1["patron_id"]
                                ]

                                +

                                x[
                                    w,
                                    dia_siguiente,
                                    p2["patron_id"]
                                ]

                                <= 1

                            )


        # =====================================
        # HORAS SEMANALES
        # =====================================

        for w in activos["id"]:

            horas = []

            for d in dias:

                for _, p in patrones.iterrows():

                    horas.append(

                        int(
                            p["duracion_norm"] * 2
                        )

                        *

                        x[
                            w,
                            d,
                            p["patron_id"]
                        ]

                    )

            total = sum(horas)

            model.Add(
                total == horas_objetivo
                #total <= horas_objetivo
            )

        trabaja_dia_var = {}

        # =====================================
        # DIAS TRABAJADOS
        # =====================================

        for w in activos["id"]:

            trabaja_dia = []

            for d in dias:

                trabaja_dia_var[w, d] = model.NewBoolVar(
                    f"trabaja_{w}_{d}"
                )

                trabaja = trabaja_dia_var[w, d]

                suma = sum(

                    x[w, d, p]

                    for p in patrones[
                        "patron_id"
                    ]

                )

                model.Add(
                    suma == trabaja
                )

                trabaja_dia.append(
                    trabaja
                )

            model.Add(
                sum(trabaja_dia)
                <= max_dias_semana
            )

        # =====================================
        # LIBRES CONSECUTIVOS
        # =====================================

        penalizacion_libres = []

        for w in activos["id"]:

            libre = {}

            for d in dias:

                libre[d] = model.NewBoolVar(
                    f"libre_{w}_{d}"
                )

                model.Add(

                    trabaja_dia_var[w, d]

                    +

                    libre[d]

                    ==

                    1

                )

            pares_consecutivos = []

            for i in range(
                len(dias) - 1
            ):

                par = model.NewBoolVar(
                    f"libres_seguidos_{w}_{i}"
                )

                d1 = dias[i]
                d2 = dias[i + 1]

                model.Add(
                    libre[d1]
                    +
                    libre[d2]
                    >= 2
                ).OnlyEnforceIf(
                    par
                )

                model.Add(
                    libre[d1]
                    +
                    libre[d2]
                    <= 1
                ).OnlyEnforceIf(
                    par.Not()
                )

                pares_consecutivos.append(
                    par
                )

            sin_libres_consecutivos = model.NewBoolVar(
                f"sin_libres_consecutivos_{w}"
            )

            model.Add(

                sum(
                    pares_consecutivos
                )

                == 0

            ).OnlyEnforceIf(
                sin_libres_consecutivos
            )

            model.Add(

                sum(
                    pares_consecutivos
                )

                >= 1

            ).OnlyEnforceIf(
                sin_libres_consecutivos.Not()
            )

            penalizacion_libres.append(

                PESO_LIBRES_CONSECUTIVOS

                *

                sin_libres_consecutivos

            )


        # =====================================
        # ABRIDOR HASTA LAS 21:00
        # =====================================

        if OBLIGAR_APERTURA_HASTA_21:

            for dia in dias:

                hora_apertura = horarios_base[
                    dia
                ]["apertura"]

                if hora_apertura is None:
                    continue

                for _, p in patrones.iterrows():

                    patron_id = p["patron_id"]

                    entrada = p["entrada_norm"]

                    duracion = float(
                        p["duracion_norm"]
                    )

                    entrada_dt = pd.to_datetime(
                        entrada,
                        format="%H:%M"
                    )

                    apertura_dt = pd.to_datetime(
                        hora_apertura,
                        format="%H:%M"
                    )

                    inicio_apertura = (

                        apertura_dt

                        -

                        pd.Timedelta(
                            minutes=
                            reglas["minutos_montaje"]
                        )

                    )

                    es_abridor = (
                        entrada_dt
                        <= inicio_apertura
                    )

                    if not es_abridor:
                        continue

                    fin_dt = (

                        entrada_dt

                        +

                        pd.Timedelta(
                            hours=duracion
                        )

                    )

                    limite = pd.to_datetime(
                        "21:00",
                        format="%H:%M"
                    )

                    if fin_dt < limite:

                        for w in activos["id"]:

                            model.Add(
                                x[
                                    w,
                                    dia,
                                    patron_id
                                ]
                                == 0
                            )

        # # =====================================
        # # CIERRE CAPACITADO
        # # =====================================

        # for _, fila in demanda.iterrows():

        #     dia = fila["dia_semana"]

        #     hora = fila["hora"]

        #     if hora != "23:30":
        #         continue

        #     cobertura_cierre = []

        #     for w in trabajadores_cierre:

        #         for p in patrones["patron_id"]:

        #             if hora in patron_horas[p]:

        #                 cobertura_cierre.append(
        #                     x[w, dia, p]
        #                 )

        #     if cobertura_cierre:

        #         model.Add(
        #             sum(cobertura_cierre)
        #             >= 1
        #         )

        # =====================================
        # MINIMO PERSONAS EN CIERRE
        # =====================================

        for dia in dias:

            hora_cierre = horarios_base[
                dia
            ]["cierre"]

            cobertura = []

            for w in activos["id"]:

                for p in patrones["patron_id"]:

                    if hora_cierre in patron_horas[p]:

                        cobertura.append(
                            x[w, dia, p]
                        )

            cobertura_fija = cobertura_bloqueada.get(
                (dia, hora_cierre),
                0
            )

            if cobertura:

                model.Add(

                    sum(cobertura)

                    +

                    cobertura_fija

                    >=

                    min_personas_cierre

                )


        # =====================================
        # APERTURA CAPACITADA
        # =====================================

        for dia in dias:

            hora_apertura = horarios_base[
                dia
            ]["apertura"]

            cobertura = []

            for w in trabajadores_apertura:

                for p in patrones["patron_id"]:

                    if hora_apertura in patron_horas[p]:

                        cobertura.append(
                            x[w, dia, p]
                        )

            if cobertura:

                model.Add(
                    sum(cobertura)
                    >= 1
                )

        # =====================================
        # CIERRE CAPACITADO
        # =====================================

        for dia in dias:

            hora_cierre = horarios_base[
                dia
            ]["cierre"]

            cobertura = []

            for w in trabajadores_cierre:

                for p in patrones["patron_id"]:

                    if hora_cierre in patron_horas[p]:

                        cobertura.append(
                            x[w, dia, p]
                        )

            if cobertura:

                model.Add(
                    sum(cobertura)
                    >= 1
                )

        # =====================================
        # COBERTURA MINIMA
        # =====================================

        for _, fila in demanda.iterrows():

            dia = fila["dia_semana"]
            hora = fila["hora"]

            cobertura = []

            for w in activos["id"]:

                for p in patrones["patron_id"]:

                    if hora in patron_horas[p]:

                        cobertura.append(
                            x[w, dia, p]
                        )

            cobertura_fija = cobertura_bloqueada.get(
                (dia, hora),
                0
            )

            if cobertura:

                model.Add(

                    sum(cobertura)

                    +

                    cobertura_fija

                    >=

                    1

                )

        # =====================================
        # MINIMO PERSONAL TARDE
        # =====================================

        if ACTIVAR_MIN_PERSONAS_TARDE:

            for _, fila in demanda.iterrows():

                dia = fila["dia_semana"]
                hora = fila["hora"]

                if (
                    HORA_INICIO_MIN_PERSONAS
                    <= hora
                    < HORA_FIN_MIN_PERSONAS
                ):

                    cobertura = []

                    for w in activos["id"]:

                        for p in patrones["patron_id"]:

                            if hora in patron_horas[p]:

                                cobertura.append(
                                    x[w, dia, p]
                                )

                    cobertura_fija = cobertura_bloqueada.get(
                        (dia, hora),
                        0
                    )

                    model.Add(
                        sum(cobertura)
                        +
                        cobertura_fija
                        >=
                        MIN_PERSONAS_TARDE
                    )

        # =====================================
        # DESCANSOS
        # =====================================

        if ACTIVAR_DESCANSOS:

            for dia in dias:

                for w in activos["id"]:

                    for p in patrones["patron_id"]:

                        hora_descanso = (
                            patron_descanso[p]
                        )

                        if hora_descanso is None:

                            continue

                        cobertura = []

                        for w2 in activos["id"]:

                            for p2 in patrones["patron_id"]:

                                if (

                                    hora_descanso
                                    in
                                    patron_horas[p2]

                                ):

                                    cobertura.append(

                                        x[
                                            w2,
                                            dia,
                                            p2
                                        ]

                                    )

                        cobertura_fija = cobertura_bloqueada.get(
                            (
                                dia,
                                hora_descanso
                            ),
                            0
                        )

                        if cobertura:

                            model.Add(

                                sum(cobertura)

                                +

                                cobertura_fija

                                >=

                                2

                            ).OnlyEnforceIf(

                                x[
                                    w,
                                    dia,
                                    p
                                ]

                            )

        # =====================================
        # FUNCION OBJETIVO
        # =====================================

        costes = []

        if modo_planificacion == "DEFICIT":

            if MODO_DEBUG:
                print(
                    "Optimizando deficit..."
                )

        else:

            if MODO_DEBUG:
                print(
                    "Optimizando exceso..."
                )
            


        # =====================================
        # DEFICITS
        # =====================================

        for _, fila in demanda.iterrows():

            dia = fila["dia_semana"]
            hora = fila["hora"]

            demanda_slot = int(
                fila["demanda"]
            )

            cobertura = []

            for w in activos["id"]:

                for p in patrones["patron_id"]:

                    if hora in patron_horas[p]:

                        cobertura.append(
                            x[w, dia, p]
                        )

            cobertura_total = (

                sum(cobertura)

                +

                cobertura_bloqueada.get(
                    (dia, hora),
                    0
                )

            )


            deficit = model.NewIntVar(
                0,
                demanda_slot,
                f"deficit_{dia}_{hora}"
            )

            model.Add(

                cobertura_total
                +
                deficit

                >=

                demanda_slot

            )

            exceso = model.NewIntVar(
                0,
                len(activos),
                f"exceso_{dia}_{hora}"
            )

            model.Add(

                cobertura_total
                - exceso

                <=

                demanda_slot

            )

            exceso_2 = model.NewBoolVar(
                f"e2_{dia}_{hora}"
            )

            exceso_3 = model.NewBoolVar(
                f"e3_{dia}_{hora}"
            )

            model.Add(
                exceso >= 2
            ).OnlyEnforceIf(
                exceso_2
            )

            model.Add(
                exceso <= 1
            ).OnlyEnforceIf(
                exceso_2.Not()
            )

            model.Add(
                exceso >= 3
            ).OnlyEnforceIf(
                exceso_3
            )

            model.Add(
                exceso <= 2
            ).OnlyEnforceIf(
                exceso_3.Not()
            )

            deficit_2 = model.NewBoolVar(
                f"d2_{dia}_{hora}"
            )

            deficit_3 = model.NewBoolVar(
                f"d3_{dia}_{hora}"
            )

            model.Add(
                deficit >= 2
            ).OnlyEnforceIf(
                deficit_2
            )

            model.Add(
                deficit <= 1
            ).OnlyEnforceIf(
                deficit_2.Not()
            )

            model.Add(
                deficit >= 3
            ).OnlyEnforceIf(
                deficit_3
            )

            model.Add(
                deficit <= 2
            ).OnlyEnforceIf(
                deficit_3.Not()
            )

            peso_relativo = int(
                100 / demanda_slot
            )

            if modo_planificacion == "DEFICIT":

                costes.append(
                    peso_relativo
                    * deficit
                )

                costes.append(
                    20
                    * peso_relativo
                    * deficit_2
                )

                costes.append(
                    200
                    * peso_relativo
                    * deficit_3
                )

            else:

                costes.append(
                    peso_relativo
                    * exceso
                )

                costes.append(
                    20
                    * peso_relativo
                    * exceso_2
                )

                costes.append(
                    200
                    * peso_relativo
                    * exceso_3
                )

        # =====================================
        # OBJETIVO
        # =====================================

        model.Minimize(

            sum(costes)
            +
            sum(
                penalizacion_libres
            )

        )

        # =====================================
        # SOLVER
        # =====================================

        solver = cp_model.CpSolver()

        solution_printer = SolutionPrinter()

        solver.parameters.max_time_in_seconds = 60

        
        if MODO_DEBUG:
            print("\nHORAS SIN PATRONES POSIBLES")

        for _, fila in demanda.iterrows():

            dia = fila["dia_semana"]
            hora = fila["hora"]

            cobertura = 0

            for p in patrones["patron_id"]:

                if hora in patron_horas[p]:
                    cobertura += 1

            if cobertura == 0:

                if MODO_DEBUG:
                    print(dia, hora)

        print("\nResolviendo...")

        status = solver.Solve(
            model,
            solution_printer
        )

        print(
            "Objetivo:",
            solver.ObjectiveValue()
        )

        print("\n===================")
        print("STATUS SOLVER")
        print("===================")

        print("status =", status)

        print(
            "OPTIMAL =",
            cp_model.OPTIMAL
        )

        print(
            "FEASIBLE =",
            cp_model.FEASIBLE
        )

        print(
            "INFEASIBLE =",
            cp_model.INFEASIBLE
        )

        print(
            "MODEL_INVALID =",
            cp_model.MODEL_INVALID
        )

        print(
            "STATUS:",
            solver.StatusName(status)
        )

        if status not in (
            cp_model.OPTIMAL,
            cp_model.FEASIBLE
        ):

            print(
                "No se encontró solución"
            )

            return None
        
        # =====================================
        # RESULTADO
        # =====================================

        resultado = []

        for w in activos["id"]:

            nombre = activos.loc[
                activos["id"] == w,
                "nombre"
            ].iloc[0]

            for d in dias:

                for _, p in patrones.iterrows():

                    if solver.Value(

                        x[
                            w,
                            d,
                            p["patron_id"]
                        ]

                    ):

                        resultado.append({

                            "worker_id": w,
                            "nombre": nombre,
                            "dia": d,
                            "entrada": p[
                                "entrada_norm"
                            ],
                            "duracion": p[
                                "duracion_norm"
                            ]

                        })


        # =====================================
        # TURNOS BLOQUEADOS
        # =====================================

        if len(turnos_bloqueados) > 0:

            for _, fila in turnos_bloqueados.iterrows():

                nombre = fila["nombre"]

                resultado.append({

                    "worker_id":
                        fila["worker_id"],

                    "nombre":
                        nombre,

                    "dia":
                        fila["dia"],

                    "entrada":
                        fila["entrada"],

                    "duracion":
                        fila["duracion"]

                })


        resultado = pd.DataFrame(
            resultado
        )

        if MODO_DEBUG:

            print("\n====================")
            print("HORAS POR TRABAJADOR")
            print("====================\n")

            for w in activos["id"]:

                horas = resultado[
                    resultado["worker_id"] == w
                ]["duracion"].sum()

                nombre = activos.loc[
                    activos["id"] == w,
                    "nombre"
                ].iloc[0]

                print(
                    f"{nombre}: {horas} h"
                )

        return resultado