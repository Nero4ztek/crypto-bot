import requests
import time
import os
from datetime import datetime

# ==========================
# VARIABLES RAILWAY
# ==========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ==========================
# CONFIGURACION
# ==========================

coins = [
    "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT",
    "ADAUSDT","DOGEUSDT","HBARUSDT","XLMUSDT",
    "XDCUSDT","ZBCUSDT","RIVERUSDT","PHNIXUSDT"
]

INTERVALO = 180  # 3 minutos

CAIDA_TEMPRANA = -0.8
CAIDA_FUERTE = -2.0
SUBIDA_FUERTE = 2.0

precios_anteriores = {}
ultima_alerta = {}

# ==========================
# TELEGRAM
# ==========================

def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print("Error Telegram:", e)

# ==========================
# BINANCE
# ==========================

def obtener_precio(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    r = requests.get(url, timeout=10)

    if r.status_code != 200:
        return None

    return float(r.json()["price"])

# ==========================
# ARRANQUE
# ==========================

inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print("Monitor cripto iniciado")

enviar_telegram(
    f"✅ Monitor Cripto 24/7 ACTIVO\nInicio: {inicio}"
)

# ==========================
# LOOP PRINCIPAL
# ==========================

while True:
    try:
        print("Revisando mercado...")

        caidas_tempranas = []
        caidas_fuertes = []
        subidas_fuertes = []

        for coin in coins:

            precio_actual = obtener_precio(coin)
            if not precio_actual:
                continue

            if coin not in precios_anteriores:
                precios_anteriores[coin] = precio_actual
                continue

            precio_anterior = precios_anteriores[coin]

            cambio = ((precio_actual - precio_anterior) / precio_anterior) * 100

            print(f"{coin}: {round(cambio,2)}%")

            ahora = time.time()

            # -------- CAIDA TEMPRANA --------
            if cambio <= CAIDA_TEMPRANA:
                if coin not in ultima_alerta or ahora - ultima_alerta[coin] > 3600:
                    caidas_tempranas.append((coin, cambio))
                    ultima_alerta[coin] = ahora

            # -------- CAIDA FUERTE --------
            if cambio <= CAIDA_FUERTE:
                if coin not in ultima_alerta or ahora - ultima_alerta[coin] > 3600:
                    caidas_fuertes.append((coin, cambio))
                    ultima_alerta[coin] = ahora

            # -------- SUBIDA FUERTE --------
            if cambio >= SUBIDA_FUERTE:
                if coin not in ultima_alerta or ahora - ultima_alerta[coin] > 3600:
                    subidas_fuertes.append((coin, cambio))
                    ultima_alerta[coin] = ahora

            precios_anteriores[coin] = precio_actual

        # ===== ALERTA TEMPRANA =====
        if len(caidas_tempranas) >= 3:
            msg = "⚠️ POSIBLE SALIDA DE LIQUIDEZ\n\n"
            for c in caidas_tempranas:
                msg += f"{c[0]} {round(c[1],2)}%\n"
            enviar_telegram(msg)

        # ===== CAIDA REAL =====
        if len(caidas_fuertes) >= 3:
            msg = "🚨 CAÍDA FUERTE DEL MERCADO\n\n"
            for c in caidas_fuertes:
                msg += f"{c[0]} {round(c[1],2)}%\n"
            enviar_telegram(msg)

        # ===== SUBIDAS =====
        if len(subidas_fuertes) >= 3:
            msg = "🚀 IMPULSO ALCISTA DETECTADO\n\n"
            for c in subidas_fuertes:
                msg += f"{c[0]} +{round(c[1],2)}%\n"
            enviar_telegram(msg)

        time.sleep(INTERVALO)

    except Exception as e:
        print("Error general:", e)
        time.sleep(60)
