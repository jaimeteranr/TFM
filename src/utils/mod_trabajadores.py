"""
Módulo encargado de gestionar la disponibilidad de trabajadores para la
planificación.

Obtiene el conjunto de trabajadores activos en función de la configuración
del sistema y de la fecha de planificación, proporcionando la información
necesaria para que el planificador genere los calendarios de trabajo.
"""

import pandas as pd

from config import USAR_FECHA_BAJA


class Trabajadores:
    """
    Gestiona la obtención de los trabajadores disponibles para la
    planificación.

    Determina qué trabajadores pueden participar en la generación del
    calendario según los criterios de activación definidos por el sistema,
    proporcionando un conjunto de empleados preparado para ser utilizado por
    los procesos de planificación.
    """

    def obtener_trabajadores_activos(
        self,
        fecha_inicio_semana
    ):

        trabajadores = pd.read_excel(
            "data/inputs/trabajadores.xlsx"
        )

        fecha = pd.to_datetime(
            fecha_inicio_semana
        )

        trabajadores["fecha_alta"] = pd.to_datetime(
            trabajadores["fecha_alta"],
            dayfirst=True
        )

        trabajadores["fecha_baja"] = pd.to_datetime(
            trabajadores["fecha_baja"],
            dayfirst=True,
            errors="coerce"
        )

        # =========================
        # MODO FECHAS
        # =========================

        if USAR_FECHA_BAJA:

            activos = trabajadores[

                (
                    trabajadores["fecha_alta"]
                    <= fecha
                )

                &

                (

                    trabajadores["fecha_baja"].isna()

                    |

                    (
                        trabajadores["fecha_baja"]
                        >= fecha
                    )

                )

            ].copy()

        # =========================
        # MODO MANUAL
        # =========================

        else:

            activos = trabajadores[

                trabajadores["Activo"] == 1

            ].copy()

        activos = activos.sort_values(
            "id"
        )

        activos = activos.reset_index(
            drop=True
        )

        print("\nDEBUG TRABAJADORES")

        print(

            activos[
                [
                    "id",
                    "nombre",
                    "Activo",
                    "apertura",
                    "cierre"
                ]
            ]

        )

        return activos