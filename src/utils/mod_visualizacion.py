import pandas as pd

from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt

from config import FECHA_INICIO_SEMANA


# =====================================
# DIAS
# =====================================

DIAS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]


# =====================================
# HORA SALIDA
# =====================================

def calcular_salida(
    entrada,
    duracion
):

    inicio = datetime.strptime(
        entrada,
        "%H:%M"
    )

    fin = inicio + timedelta(
        hours=float(duracion)
    )

    return fin.strftime(
        "%H:%M"
    )


# =====================================
# VISUALIZACION
# =====================================

def generar_visualizacion():

    calendario = pd.read_excel(
        "data/outputs/calendario_generado.xlsx"
    )

    # -------------------------
    # Turno texto
    # -------------------------

    calendario["turno"] = calendario.apply(
        lambda x:
        f"{x['entrada']} - "
        f"{calcular_salida(x['entrada'], x['duracion'])}",
        axis=1
    )

    # -------------------------
    # Tabla
    # -------------------------

    tabla = calendario.pivot(
        index="nombre",
        columns="dia",
        values="turno"
    )

    tabla = tabla.reindex(
        columns=DIAS
    )

    tabla = tabla.fillna(
        "L"
    )

    # -------------------------
    # Mostrar pantalla
    # -------------------------

    print("\n========================")
    print("HORARIO VISUAL")
    print("========================\n")

    print(
        tabla.to_string()
    )

    # -------------------------
    # Guardar
    # -------------------------

    tabla.to_excel(
        "data/outputs/horario_visual.xlsx"
    )

    print(
        "\nGuardado data/outputs/horario_visual.xlsx"
    )

    # =====================================
    # IMAGEN
    # =====================================

    fig, ax = plt.subplots(
        figsize=(18, 6)
    )

    ax.axis("off")

    tabla_grafica = tabla.reset_index()

    from datetime import timedelta

    fecha_inicio = pd.to_datetime(
        FECHA_INICIO_SEMANA
    )

    dias_es = {
        "Monday": "LUNES",
        "Tuesday": "MARTES",
        "Wednesday": "MIÉRCOLES",
        "Thursday": "JUEVES",
        "Friday": "VIERNES",
        "Saturday": "SÁBADO",
        "Sunday": "DOMINGO"
    }

    cabeceras = ["TRABAJADOR"]

    for i, dia in enumerate(tabla.columns):

        fecha = fecha_inicio + timedelta(
            days=i
        )

        cabeceras.append(

            dias_es[dia]

            +

            "\n"

            +

            fecha.strftime(
                "%d/%m"
            )

        )

    colores_trabajadores = [
        "#FFF7CC",
        "#DFF2D3",
        "#DCEEFF",
        "#E9DDFC",
        "#FCE8C9",
        "#F8D6E8",
        "#D6F4EF",
        "#DCEEFF",
        "#FFF3D6",
        "#FFDCCF",
        "#E6F7D4",
        "#D4EAF7",
        "#F2D4F7",
        "#F7E7D4",
        "#D4F7EA",
        "#F7D4D4",
        "#E1D4F7",
        "#D4F7F3",
        "#F7F1D4",
        "#D4E3F7"
    ]

    gris_libre = "#E8E8E8"

    tabla_plot = ax.table(
        cellText=tabla_grafica.values,
        colLabels=cabeceras,
        cellLoc="center",
        loc="center"
    )

    # =====================================
    # CABECERA
    # =====================================

    azul_oscuro = "#1F3A5F"

    azul_claro = "#C8D6E8"

    for col in range(
        len(cabeceras)
    ):

        celda = tabla_plot[
            (0, col)
        ]

        texto = celda.get_text()

        texto.set_weight(
            "bold"
        )

        texto.set_fontsize(
            12
        )

        if col == 0:

            celda.set_facecolor(
                azul_oscuro
            )

            texto.set_color(
                "white"
            )

        else:

            celda.set_facecolor(
                azul_claro
            )

            texto.set_color(
                "#1F2F4A"
            )

    # =====================================
    # COLORES POR TRABAJADOR
    # =====================================

    for fila in range(1, len(tabla_grafica) + 1):

        color = colores_trabajadores[
            (fila - 1)
            % len(colores_trabajadores)
        ]

        for col in range(
            1,
            len(tabla_grafica.columns)
        ):

            celda = tabla_plot[
                (fila, col)
            ]

            texto = celda.get_text().get_text()

            if texto == "L":

                celda.set_facecolor(
                    gris_libre
                )

            else:

                celda.set_facecolor(
                    color
                )
                
    # =====================================
    # COLUMNA TRABAJADOR
    # =====================================

    for fila in range(
        1,
        len(tabla_grafica) + 1
    ):

        tabla_plot[
            (fila, 0)
        ].set_facecolor(
            "white"
        )

    tabla_plot.auto_set_font_size(
        False
    )

    tabla_plot.set_fontsize(
        8
    )

    tabla_plot.scale(
        0.8,
        2.6
    )

    # =====================================
    # TRABAJADORES
    # =====================================

    for fila in range(1, len(tabla_grafica) + 1):

        celda = tabla_plot[(fila, 0)]

        texto = celda.get_text()

        texto.set_text(
            texto.get_text().upper()
        )

        texto.set_fontsize(
            10
        )

        texto.set_weight(
            "bold"
        )

    titulo = (

        "VACANZE ROMANE - HORARIO SEMANA "

        +

        pd.to_datetime(
            FECHA_INICIO_SEMANA
        ).strftime(
            "%d-%m-%Y"
        )

    )

    plt.title(
        titulo,
        fontsize=18,
        pad=25,
        fontweight="bold"
    )

    plt.savefig(
        "data/outputs/horario_visual.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    print(
        "Guardado horario_visual.png"
    )

    return tabla