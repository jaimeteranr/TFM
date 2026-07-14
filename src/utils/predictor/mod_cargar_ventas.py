import pandas as pd
from pathlib import Path


class VentasLoader:

    def __init__(
        self,
        carpeta="data/sales"
    ):

        self.carpeta = Path(carpeta)

    def cargar(self):

        archivos = sorted(
            self.carpeta.glob("*.xlsx")
        )

        dfs = []

        for archivo in archivos:

            df = pd.read_excel(archivo)

            dfs.append(df)

        ventas = pd.concat(
            dfs,
            ignore_index=True
        )

        ventas["Fecha"] = pd.to_datetime(
            ventas["Fecha"],
            format="%d/%m/%Y"
        )

        ventas = ventas.sort_values(
            "Fecha"
        ).reset_index(drop=True)

        return ventas