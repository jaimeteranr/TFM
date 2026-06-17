import pandas as pd

from config import *

# =====================================
# CARGAR REGLAS
# =====================================

def cargar_reglas():

    df = pd.read_excel(
        "data/inputs/reglas_local.xlsx"
    )

    reglas = dict(
        zip(
            df["parametro"],
            df["valor"]
        )
    )

    return reglas


# =====================================
# MOSTRAR REGLAS
# =====================================

def mostrar_reglas(reglas):

    print("\n========================")
    print("REGLAS")
    print("========================\n")

    for k, v in reglas.items():

        print(
            f"{k}: {v}"
        )