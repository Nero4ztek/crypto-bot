import requests
import time
import os

# ==========================
# TELEGRAM DESDE RAILWAY
# ==========================
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ==========================
# MONEDAS A ANALIZAR
# ==========================
coins = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "HBARUSDT",   # Hedera
    "XLMUSDT",    # Stellar
    "XDCUSDT",
    "ZBCUSDT",    # Zebec
    "RIVERUSDT",
    "PHNIXUSDT"   # Phoenix
]

# ==========================
INTERVALO = 300  # 5 minutos
CAIDA_ALERTA = -3

volumen_anterior = {}
alertas_enviadas = {}

# ==========================
def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": mensaje
    }
    requests.post(url, data=data)


def obtener_data(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    r = requests.get(url)
    data = r.json()

    precio = float(data["priceChangePercent"])
    volumen = float(data["quoteVolume"])

    return precio, volumen


print("🚀 Monitor 24/7 iniciado...")

while True:
    try:
        caidas = []
        movimientos_tempranos = []

        for coin in coins:
            precio, volumen = obtener_data(coin)

            # ===== ALERTA CAÍDA GENERAL =====
            if precio <= CAIDA_ALERTA:
                caidas.append((coin, precio))

            # ===== DETECTOR TEMPRANO =====
            if coin in volumen_anterior:
                cambio_volumen = (
                    (volumen - volumen_anterior[coin])
                    / volumen_anterior[coin]
                ) * 100

                if cambio_volumen > 20 and abs(precio) < 3:

                    # evita spam
                    if coin not in alertas_enviadas:
                        movimientos_tempranos.append(
                            f"{coin}\nVolumen +{round(cambio_volumen,2)}%\nPrecio {round(precio,2)}%"
                        )
                        alertas_enviadas[coin] = time.time()

            volumen_anterior[coin] = volumen

        # ===== ALERTA MERCADO EN MIEDO =====
        if len(caidas) >= 3:
            mensaje = "⚠️ MERCADO EN CAÍDA\n\n"
            for coin, cambio in caidas:
                mensaje += f"{coin}: {round(cambio,2)}%\n"

            enviar_telegram(mensaje)

        # ===== ALERTA MOVIMIENTO TEMPRANO =====
        if movimientos_tempranos:
            mensaje = "🚨 POSIBLE MOVIMIENTO TEMPRANO\n\n"
            mensaje += "\n\n".join(movimientos_tempranos)
            enviar_telegram(mensaje)

        # limpia alertas cada 1 hora
        ahora = time.time()
        alertas_enviadas = {
            c: t for c, t in alertas_enviadas.items()
            if ahora - t < 3600
        }

        time.sleep(INTERVALO)

    except Exception as e:
        print("Error:", e)
        time.sleep(60)
