import pandas as pd

from config import USAR_TURNOS_BLOQUEADOS


class TurnosBloqueados:

    def cargar_turnos_bloqueados(
        self
    ):

        if not USAR_TURNOS_BLOQUEADOS:

            return pd.DataFrame()

        try:

            df = pd.read_excel(
                "data/inputs/turnos_bloqueados.xlsx"
            )

            # =========================
            # DIA NUMÉRICO -> TEXTO
            # =========================

            mapa_dias = {

                1: "Monday",
                2: "Tuesday",
                3: "Wednesday",
                4: "Thursday",
                5: "Friday",
                6: "Saturday",
                7: "Sunday"

            }

            df["dia"] = df["dia"].map(
                mapa_dias
            )

            # =========================
            # NORMALIZAR HORA
            # =========================

            df["entrada"] = (

                df["entrada"]

                .astype(str)

                .str[:5]

            )

            return df

        except Exception as e:

            print(
                "Error cargando turnos bloqueados:",
                e
            )

            return pd.DataFrame()