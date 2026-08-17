# =====================================
# SEMANA A PLANIFICAR
# =====================================

FECHA_INICIO_SEMANA = "2026-08-24" # Formato: "YYYY-MM-DD"

# =====================================
# SOLVER
# =====================================

MODO_SOLVER = "LIBRE" # "LIBRE" o "PATRONES"

# =====================================
# DEMANDA
# =====================================

MODO_DEMANDA = "PREDICCION" # "HISTORICA" o "PREDICCION"

# =====================================
# MODELO DE PREDICCIÓN
# =====================================

MODELO_PREDICCION = "xgboost"

# Opciones:
# "xgboost"
# "lstm"
# "random_forest"
# "decision_tree"

TIPO_PREDICCION = "mensual"

# Opciones:
# "estacional"
# "completa"
# "mensual"

# =====================================
# DIVISIÓN TRAIN / TEST
# =====================================

TIPO_SPLIT = "mensual"

# Opciones:
# "mensual" 1 semana al mes para test
# "temporal" 25% final para test

# =====================================
# DEBUG:
# - MODO_DEBUG: Si es True, se mostrarán mensajes de depuración adicionales.
# =====================================

MODO_DEBUG = False

# =====================================
# MOSTRAR_CALENDARIO: Si es True, se mostrará un calendario visual de la semana planificada.
# ===================================== 
MOSTRAR_CALENDARIO = True

# =====================================
# PERMITIR_VARIANTES_ENTRADA: Si es True, se permitirá modificar en media hora las entradas de los patrones históricos.
# =====================================

PERMITIR_VARIANTES_ENTRADA = True

# =====================================
# PERMITIR_VARIANTES_DURACION: Si es True, se permitirá modificar en media hora las duraciones de los patrones históricos.
# =====================================

PERMITIR_VARIANTES_DURACION = True

# =====================================
# DESCANSOS
# =====================================

ACTIVAR_DESCANSOS = True

# =====================================
# SELECCION TRABAJADORES
# =====================================

USAR_FECHA_BAJA = False

# =====================================
# TURNOS BLOQUEADOS, SI SE QUIERE USAR, DEBE EXISTIR EL ARCHIVO "turnos_bloqueados.xlsx"
# =====================================

USAR_TURNOS_BLOQUEADOS = False

# =====================================
# PESO PARA PREMIAR DIAS LIBRES JUNTOS
# =====================================

PESO_LIBRES_CONSECUTIVOS = 5000

# =====================================
# Cada persona que abra por la mañana se queda hasta las 21:00
# =====================================

OBLIGAR_APERTURA_HASTA_21 = True

# =====================================
# MINIMO PERSONAL TARDE
# =====================================

ACTIVAR_MIN_PERSONAS_TARDE = True

MIN_PERSONAS_TARDE = 2

HORA_INICIO_MIN_PERSONAS = "15:00"
HORA_FIN_MIN_PERSONAS = "21:00"