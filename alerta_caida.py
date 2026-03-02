import requests
import time
import os
from datetime import datetime

# ==========================
# VARIABLES DESDE RAILWAY
# ==========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ==========================
# CONFIGURACION
# ==========================

coins = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "HBARUSDT",
    "XLMUSDT",
    "XDCUSDT",
    "ZBCUSDT",
    "RIVERUSDT",
    "PHNIXUSDT"
]

CAIDA_ALERTA = -3        # caída mercado %
VOLUMEN_ALERTA = 20      # aumento volumen %
INTERVALO = 300          # 5 minutos

ultima_alerta = {}

# ==========================
# TELEGRAM
# ==========================

def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": mensaje
        }
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print("Error Telegram:", e)

# ==========================
# BINANCE DATA
# ==========================

def obtener_data(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    r = requests.get(url, timeout=10)

    if r.status_code != 200:
        return None

    data = r.json()

    return {
        "change": float(data["priceChangePercent"]),
        "volume": float(data["volume"])
    }

# ==========================
# MENSAJE DE ARRANQUE
# ==========================

inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print("Monitor cripto iniciado")

enviar_telegram(
    f"✅ Monitor Cripto 24/7 ACTIVO\n\nInicio: {inicio}"
)

# ==========================
# LOOP PRINCIPAL
# ==========================

while True:
    try:
        print("Revisando mercado...")

        caidas = []
        movimientos_tempranos = []

        for coin in coins:

            data = obtener_data(coin)

            if not data:
                continue

            cambio = data["change"]
            volumen = data["volume"]

            print(f"{coin}: {cambio}%")

            # -------- ALERTA CAIDA --------
            if cambio <= CAIDA_ALERTA:
                caidas.append((coin, cambio))

            # -------- ALERTA VOLUMEN TEMPRANO --------
            if abs(cambio) < 3 and volumen > 0:
                if coin not in ultima_alerta or time.time() - ultima_alerta[coin] > 3600:
                    movimientos_tempranos.append((coin, cambio))
                    ultima_alerta[coin] = time.time()

        # ===== ALERTA MERCADO =====
        if len(caidas) >= 3:
            mensaje = "⚠️ MERCADO EN CAÍDA\n\n"

            for coin, cambio in caidas:
                mensaje += f"{coin}: {round(cambio,2)}%\n"

            enviar_telegram(mensaje)

        # ===== ALERTA MOVIMIENTO =====
        for coin, cambio in movimientos_tempranos:
            mensaje = (
                "🚨 POSIBLE MOVIMIENTO TEMPRANO\n\n"
                f"{coin}\n"
                f"Cambio: {round(cambio,2)}%"
            )
            enviar_telegram(mensaje)

        time.sleep(INTERVALO)

    except Exception as e:
        print("Error general:", e)
        time.sleep(60)
