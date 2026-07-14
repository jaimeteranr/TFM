import pandas as pd


class SchedulerConfig:

    def __init__(
        self,
        fichero="data/inputs/reglas_local.xlsx"
    ):

        self.fichero = fichero

        self.reglas = None

    def cargar(self):

        df = pd.read_excel(
            self.fichero
        )

        self.reglas = dict(

            zip(

                df["parametro"],

                df["valor"]

            )

        )

        return self.reglas

    def mostrar(self):

        print("\n========================")
        print("REGLAS")
        print("========================\n")

        for k, v in self.reglas.items():

            print(
                f"{k}: {v}"
            )