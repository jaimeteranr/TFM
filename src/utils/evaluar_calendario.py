import pandas as pd

# =====================================
# CARGA
# =====================================

calendario = pd.read_excel(
    "calendario_generado.xlsx"
)

demanda = pd.read_excel(
    "demanda_verano.xlsx"
)

patrones = pd.read_excel(
    "catalogo_patrones.xlsx"
)

cobertura_patrones = pd.read_excel(
    "cobertura_patrones.xlsx"
)

# =====================================
# MAPA PATRON -> HORAS
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
# RECUPERAR patron_id
# =====================================

calendario = calendario.merge(
    patrones[
        [
            "patron_id",
            "entrada_norm",
            "duracion_norm"
        ]
    ],
    left_on=[
        "entrada",
        "duracion"
    ],
    right_on=[
        "entrada_norm",
        "duracion_norm"
    ],
    how="left"
)

# =====================================
# COBERTURA REAL
# =====================================

cobertura_dict = {}

for _, fila in calendario.iterrows():

    dia = fila["dia"]

    patron_id = fila["patron_id"]

    horas = patron_horas[
        patron_id
    ]

    for hora in horas:

        clave = (
            dia,
            hora
        )

        cobertura_dict[
            clave
        ] = cobertura_dict.get(
            clave,
            0
        ) + 1

# =====================================
# EVALUACION
# =====================================

registros = []

for _, fila in demanda.iterrows():

    dia = fila["dia_semana"]
    hora = fila["hora"]

    demanda_slot = int(
        fila["demanda"]
    )

    cobertura = cobertura_dict.get(
        (dia, hora),
        0
    )

    deficit = max(
        0,
        demanda_slot - cobertura
    )

    exceso = max(
        0,
        cobertura - demanda_slot
    )

    registros.append({

        "dia": dia,
        "hora": hora,
        "demanda": demanda_slot,
        "cobertura": cobertura,
        "deficit": deficit,
        "exceso": exceso
    })

evaluacion = pd.DataFrame(
    registros
)

# =====================================
# ESTADISTICAS
# =====================================

print("\n====================")
print("RESUMEN")
print("====================\n")

print(
    "Demanda total:",
    evaluacion["demanda"].sum()
)

print(
    "Cobertura total:",
    evaluacion["cobertura"].sum()
)

print(
    "Deficit total:",
    evaluacion["deficit"].sum()
)

print(
    "Deficit maximo:",
    evaluacion["deficit"].max()
)

print(
    "Exceso total:",
    evaluacion["exceso"].sum()
)

print(
    "Exceso maximo:",
    evaluacion["exceso"].max()
)

print(
    "Slots con deficit >= 1:",
    (
        evaluacion["deficit"] >= 1
    ).sum()
)

print(
    "Slots con deficit >= 2:",
    (
        evaluacion["deficit"] >= 2
    ).sum()
)

print(
    "Slots con deficit >= 3:",
    (
        evaluacion["deficit"] >= 3
    ).sum()
)



print(
    "Cobertura media:",
    round(
        100
        *
        evaluacion["cobertura"].sum()
        /
        evaluacion["demanda"].sum(),
        2
    ),
    "%"
)

# =====================================
# PEORES SLOTS
# =====================================

print("\n====================")
print("PEORES SLOTS")
print("====================\n")

print(

    evaluacion

    .sort_values(
        [
            "deficit",
            "exceso",
            "demanda"
        ],
        ascending=False
    )

    .head(30)

)

# =====================================
# EXPORTAR
# =====================================

evaluacion.to_excel(
    "evaluacion_calendario.xlsx",
    index=False
)

print(
    "\nGuardado evaluacion_calendario.xlsx"
)