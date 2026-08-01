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
from datetime import datetime, timedelta


class SolverPatrones:
    """
    Resuelve el problema de asignación de turnos mediante optimización.

    Construye y ejecuta el modelo de planificación a partir de la información
    disponible sobre trabajadores, patrones de turno, demanda y reglas del
    sistema, obteniendo un calendario de trabajo que satisface las
    restricciones definidas y optimiza los criterios establecidos para la
    planificación.
    """
    def _preprocesar(self):

        # =====================================
        # DIAS
        # =====================================

        self.dias = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]

        self.worker_ids = self.activos["id"].tolist()
        self.patron_ids = self.patrones["patron_id"].tolist()

        self.trabajadores_apertura = self.activos[
            self.activos["apertura"] == 1
        ]["id"].tolist()

        self.trabajadores_cierre = self.activos[
            self.activos["cierre"] == 1
        ]["id"].tolist()

        # =====================================
        # REGLAS
        # =====================================

        self.horas_semanales = int(
            self.reglas["horas_semanales"]
        )

        self.max_dias_semana = int(
            self.reglas["max_dias_semana"]
        )

        self.descanso_entre_turnos = int(
            self.reglas["descanso_entre_turnos"]
        )

        self.min_personas_cierre = int(
            self.reglas["min_personas_cierre"]
        )

        self.horas_objetivo = (
            self.horas_semanales * 2
        )

        # =====================================
        # PATRON -> HORAS
        # =====================================

        self.patron_horas = {}

        for patron_id in self.patron_ids:

            self.patron_horas[patron_id] = list(

                self.cobertura_patrones[
                    self.cobertura_patrones["patron_id"]
                    == patron_id
                ]["hora"]

            )
        
        # =====================================
        # PATRON -> HORA DESCANSO
        # =====================================

        self.patron_descanso = {}

        for _, fila in self.patrones.iterrows():

            patron_id = fila["patron_id"]

            duracion = float(
                fila["duracion_norm"]
            )

            if duracion <= 6:

                self.patron_descanso[
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

            self.patron_descanso[
                patron_id
            ] = instante_descanso.strftime(
                "%H:%M"
            )

        # =====================================
        # INFORMACION DE PATRONES
        # =====================================

        self.entrada_patron = (
            self.patrones
            .set_index("patron_id")["entrada_norm"]
            .to_dict()
        )

        self.duracion_patron = (
            self.patrones
            .set_index("patron_id")["duracion_norm"]
            .to_dict()
        )

        self.nombre_trabajador = (
            self.activos
            .set_index("id")["nombre"]
            .to_dict()
        )

        # =====================================
        # INICIO Y FIN DE PATRONES
        # =====================================

        self.inicio_patron = {}
        self.fin_patron = {}

        for p in self.patron_ids:

            inicio = pd.to_datetime(
                self.entrada_patron[p],
                format="%H:%M"
            )

            fin = inicio + pd.Timedelta(
                hours=float(self.duracion_patron[p])
            )

            self.inicio_patron[p] = inicio
            self.fin_patron[p] = fin

        self.duracion_bloques = {
            p: int(self.duracion_patron[p] * 2)
            for p in self.patron_ids
        }

        self.cubre_21 = {}

        limite = pd.to_datetime("21:00", format="%H:%M")

        for p in self.patron_ids:
            self.cubre_21[p] = (
                self.fin_patron[p] >= limite
            )

        # =====================================
        # HORA -> PATRONES
        # =====================================

        self.patrones_por_hora = {}

        for hora in self.cobertura_patrones["hora"].unique():

            self.patrones_por_hora[hora] = (
                self.cobertura_patrones[
                    self.cobertura_patrones["hora"] == hora
                ]["patron_id"].tolist()
            )

        self.horarios_dia = {}
        self.dias_abiertos = []

        for dia, info in self.horarios_base.items():

            # Tienda cerrada ese día
            if not info["apertura"] or not info["cierre"]:
                continue

            self.dias_abiertos.append(dia)

            apertura = datetime.strptime(
                info["apertura"],
                "%H:%M"
            )

            cierre = datetime.strptime(
                info["cierre"],
                "%H:%M"
            )

            if cierre <= apertura:
                cierre += timedelta(days=1)

            self.horarios_dia[dia] = (apertura, cierre)

        if MODO_DEBUG:
            print(self.patrones.columns)

            print(
                self.patrones[
                    (self.patrones["entrada_norm"] == "17:00") &
                    (self.patrones["duracion_norm"] == 9.0)
                ]
            )



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
        # PARAMETROS
        # =====================================

        self.activos = activos
        self.demanda = demanda
        self.patrones = patrones
        self.cobertura_patrones = cobertura_patrones
        self.reglas = reglas
        self.modo_planificacion = modo_planificacion
        self.turnos_bloqueados = turnos_bloqueados
        self.horarios_base = horarios_base
        self.temporada = temporada

        self._preprocesar()

        # OR-Tools trabaja en bloques de 30 min


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
                self.demanda.groupby("dia_semana")["demanda"].sum()
            )

            print("\nDEMANDA VIERNES TARDE")
            print(
                self.demanda[
                    (self.demanda["dia_semana"] == "Friday")
                    &
                    (self.demanda["hora"] >= "00:00")
                ]
            )

            print("\nDEMANDA SABADO TARDE")
            print(
                self.demanda[
                    (self.demanda["dia_semana"] == "Saturday")
                    &
                    (self.demanda["hora"] >= "00:00")
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

        for w in self.worker_ids:

            for d in self.dias:

                for p in self.patron_ids:

                    x[w, d, p] = model.NewBoolVar(
                        f"x_{w}_{d}_{p}"
                    )
                    
        # =====================================
        # PATRONES FUERA DE HORARIO
        # =====================================

        for dia in self.dias_abiertos:

            apertura, cierre = self.horarios_dia[dia]

            apertura -= timedelta(
                minutes=self.reglas["minutos_montaje"]
            )

            cierre += timedelta(
                minutes=self.reglas["minutos_recogida"]
            )

            for p in self.patron_ids:

                inicio = self.inicio_patron[p]
                fin = self.fin_patron[p]

                # Si el patrón cruza medianoche
                if fin <= inicio:
                    fin += timedelta(days=1)

                if inicio < apertura or fin > cierre:

                    for w in self.worker_ids:

                        model.Add(
                            x[w, dia, p] == 0
                        )

        # =====================================
        # MAX 1 TURNO POR DIA
        # =====================================

        for w in self.worker_ids:

            for d in self.dias:

                model.Add(

                    sum(
                        x[w, d, p]
                        for p in self.patron_ids
                    )

                    <= 1

                )

        # =====================================
        # LIBRANZAS FIN DE SEMANA
        # =====================================

        trabajan_sabado = []
        trabajan_domingo = []

        for w in self.worker_ids:

            trabaja_sabado = model.NewBoolVar(
                f"sabado_{w}"
            )

            trabaja_domingo = model.NewBoolVar(
                f"domingo_{w}"
            )

            model.Add(

                sum(
                    x[w, "Saturday", p]
                    for p in self.patron_ids
                )

                >= 1

            ).OnlyEnforceIf(
                trabaja_sabado
            )

            model.Add(

                sum(
                    x[w, "Saturday", p]
                    for p in self.patron_ids
                )

                == 0

            ).OnlyEnforceIf(
                trabaja_sabado.Not()
            )

            model.Add(

                sum(
                    x[w, "Sunday", p]
                    for p in self.patron_ids
                )

                >= 1

            ).OnlyEnforceIf(
                trabaja_domingo
            )

            model.Add(

                sum(
                    x[w, "Sunday", p]
                    for p in self.patron_ids
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
                == len(self.activos) - 1
            )

            model.Add(
                sum(trabajan_domingo)
                == len(self.activos) - 1
            )

        else:

            model.Add(
                sum(trabajan_sabado)
                == len(self.activos)
            )

            model.Add(
                sum(trabajan_domingo)
                == len(self.activos)
            )

        # =====================================
        # DESCANSO ENTRE TURNOS
        # =====================================

        for w in self.worker_ids:

            for i in range(
                len(self.dias) - 1
            ):

                dia_actual = self.dias[i]

                dia_siguiente = self.dias[i + 1]

                for p1 in self.patron_ids:

                    fin1 = self.fin_patron[p1]

                    for p2 in self.patron_ids:

                        inicio2 = (
                            self.inicio_patron[p2]
                            +
                            pd.Timedelta(days=1)
                        )

                        horas_descanso = (
                            inicio2
                            -
                            fin1
                        ).total_seconds() / 3600

                        if horas_descanso < self.descanso_entre_turnos:

                            model.Add(
                                x[w, dia_actual, p1]
                                +
                                x[w, dia_siguiente, p2]
                                <= 1
                            )


        # =====================================
        # HORAS SEMANALES
        # =====================================

        for w in self.worker_ids:

            horas = []

            for d in self.dias:
                for p in self.patron_ids:
                    horas.append(
                        self.duracion_bloques[p]
                        *
                        x[w,d,p]
                    )

            total = sum(horas)

            model.Add(
                total == self.horas_objetivo
                #total <= self.horas_objetivo
            )

        trabaja_dia_var = {}

        # =====================================
        # DIAS TRABAJADOS
        # =====================================

        for w in self.worker_ids:

            trabaja_dia = []

            for d in self.dias:

                trabaja_dia_var[w, d] = model.NewBoolVar(
                    f"trabaja_{w}_{d}"
                )

                trabaja = trabaja_dia_var[w, d]

                suma = sum(

                    x[w, d, p]

                    for p in self.patrones[
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
                <= self.max_dias_semana
            )

        # =====================================
        # LIBRES CONSECUTIVOS
        # =====================================

        penalizacion_libres = []

        for w in self.worker_ids:

            libre = {}

            for d in self.dias:

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
                len(self.dias) - 1
            ):

                par = model.NewBoolVar(
                    f"libres_seguidos_{w}_{i}"
                )

                d1 = self.dias[i]
                d2 = self.dias[i + 1]

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

            limite_21 = pd.to_datetime(
                "21:00",
                format="%H:%M"
            )

            for dia in self.dias_abiertos:

                if not self.horarios_base[dia]["abierto"]:
                    continue

                apertura, _ = self.horarios_dia[dia]

                apertura -= timedelta(
                    minutes=self.reglas["minutos_montaje"]
                )

                candidatos = []

                for p in self.patron_ids:

                    if (
                        self.inicio_patron[p] <= apertura
                        and
                        self.fin_patron[p] >= limite_21
                    ):

                        for w in self.trabajadores_apertura:

                            candidatos.append(
                                x[w, dia, p]
                            )

                if candidatos:

                    model.Add(
                        sum(candidatos) >= 1
                    )

        # =====================================
        # MINIMO PERSONAS EN CIERRE
        # =====================================

        for dia in self.dias_abiertos:

            _, cierre = self.horarios_dia[dia]

            hora_cierre = (cierre + timedelta(minutes=self.reglas["minutos_recogida"])
            ).strftime("%H:%M")

            cobertura = []

            for w in self.worker_ids:

                for p in self.patron_ids:

                    if hora_cierre in self.patron_horas[p]:

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
                    self.min_personas_cierre
                )

        # =====================================
        # APERTURA CAPACITADA
        # =====================================

        for dia in self.dias_abiertos:

            hora_apertura = self.horarios_base[
                dia
            ]["apertura"]

            cobertura = []

            for w in self.trabajadores_apertura:

                for p in self.patron_ids:

                    if hora_apertura in self.patron_horas[p]:

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

        for dia in self.dias_abiertos:

            _, cierre = self.horarios_dia[dia]

            hora_cierre = (cierre + timedelta(minutes=self.reglas["minutos_recogida"])
            ).strftime("%H:%M")

            cobertura = []

            for w in self.trabajadores_cierre:

                for p in self.patron_ids:

                    if hora_cierre in self.patron_horas[p]:

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

        for _, fila in self.demanda.iterrows():
            
            dia = fila["dia_semana"]

            if dia not in self.dias_abiertos:
                continue

            hora = fila["hora"]

            cobertura = []

            for w in self.worker_ids:

                for p in self.patrones_por_hora.get(hora, []):

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

            for _, fila in self.demanda.iterrows():

                dia = fila["dia_semana"]

                if dia not in self.dias_abiertos:
                    continue

                hora = fila["hora"]

                if (
                    HORA_INICIO_MIN_PERSONAS
                    <= hora
                    < HORA_FIN_MIN_PERSONAS
                ):

                    cobertura = []

                    for w in self.worker_ids:
                        for p in self.patrones_por_hora.get(hora, []):

                            cobertura.append(
                                x[w, dia, p]
                            )

                    cobertura_fija = cobertura_bloqueada.get(
                        (dia, hora),
                        0
                    )

                    if MODO_DEBUG:
                        print("\n", dia)
                        print("Hora cierre:", hora_cierre)
                        print("Cobertura fija:", cobertura_fija)

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

            for dia in self.dias_abiertos:

                for w in self.worker_ids:

                    for p in self.patron_ids:

                        hora_descanso = (
                            self.patron_descanso[p]
                        )

                        if hora_descanso is None:

                            continue

                        cobertura = []

                        for w2 in self.worker_ids:

                            for p2 in self.patron_ids:

                                if (

                                    hora_descanso
                                    in
                                    self.patron_horas[p2]

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

        for _, fila in self.demanda.iterrows():

            dia = fila["dia_semana"]

            if dia not in self.dias_abiertos:
                continue

            hora = fila["hora"]

            demanda_slot = int(
                fila["demanda"]
            )

            cobertura = []

            for w in self.worker_ids:
                
                for p in self.patrones_por_hora.get(hora, []):

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
                len(self.activos),
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

            # =====================================
            # COSTE DE COBERTURA
            # =====================================

            # Cuanto menor es la demanda, más importante es cubrirla al 100%
            peso_relativo = max(1, int(10 / demanda_slot))

            costes.append(
                100 * peso_relativo * deficit
            )

            costes.append(
                10 * exceso
            )

            costes.append(
                500 * peso_relativo * deficit_2
            )

            costes.append(
                2000 * peso_relativo * deficit_3
            )

            costes.append(
                50 * exceso_2
            )

            costes.append(
                200 * exceso_3
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

        for _, fila in self.demanda.iterrows():

            dia = fila["dia_semana"]

            if dia not in self.dias_abiertos:
                continue

            hora = fila["hora"]

            cobertura = 0

            for p in self.patron_ids:

                if hora in self.patron_horas[p]:
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

        for w in self.worker_ids:

            nombre = self.nombre_trabajador[w]

            for d in self.dias:

                for p in self.patron_ids:

                    if solver.Value(x[w, d, p]):

                        resultado.append({

                            "worker_id": w,
                            "nombre": nombre,
                            "dia": d,
                            "entrada": self.entrada_patron[p],
                            "duracion": self.duracion_patron[p]

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

            for w in self.worker_ids:

                horas = resultado[
                    resultado["worker_id"] == w
                ]["duracion"].sum()

                nombre = self.activos.loc[
                    self.activos["id"] == w,
                    "nombre"
                ].iloc[0]

                print(
                    f"{nombre}: {horas} h"
                )

        return resultado