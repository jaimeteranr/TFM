from pathlib import Path
import joblib

from tensorflow.keras.models import load_model

# from tensorflow.keras.models import load_model


# ============================================================
# RUTAS
# ============================================================

BASE_PATH = Path(__file__).resolve().parent.parent

LSTM_MODEL_PATH = (
    BASE_PATH
    / "models"
    / "modelo_lstm.keras"
)

SCALER_X_PATH = (
    BASE_PATH
    / "models"
    / "scaler_X.pkl"
)

SCALER_Y_PATH = (
    BASE_PATH
    / "models"
    / "scaler_y.pkl"
)


# ============================================================
# CLASE
# ============================================================

class CalendarPredictorLSTM:

    def __init__(self):

        print("Cargando modelo...")

        self.model = load_model(
            LSTM_MODEL_PATH
        )

        print("Modelo cargado correctamente.")

        print(
            "Entrada:",
            self.model.input_shape
        )

        print(
            "Salida:",
            self.model.output_shape
        )

        print()
        print("Cargando scaler X...")

        self.scaler_X = joblib.load(
            SCALER_X_PATH
        )

        print("Scaler X cargado correctamente.")

        print()
        print("Cargando scaler Y...")

        self.scaler_y = joblib.load(
            SCALER_Y_PATH
        )

        print("Scaler Y cargado correctamente.")

    # ========================================================
    # PREDICCIÓN
    # ========================================================

    def predecir(
        self,
        historico,
        fecha_inicio,
        fecha_fin,
        eventos
    ):

        print()
        print("================================")
        print("LSTM - INICIO PREDICCIÓN")
        print("================================")

        print(
            "Histórico:",
            historico.shape
        )

        print()
        print("Columnas:")

        print(
            historico.columns.tolist()
        )

        print()
        print("Últimas 30 filas:")

        print(
            historico.tail(30)
        )

        print()
        print(
            "Fecha inicio:",
            fecha_inicio
        )

        print(
            "Fecha fin:",
            fecha_fin
        )

        print()
        print(
            "Número de eventos:",
            len(eventos)
        )

        raise Exception(
            "PARADA DE DEPURACIÓN LSTM"
        )