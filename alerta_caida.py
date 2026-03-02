import requests
import time
import os

# ==========================
# CONFIGURACION TELEGRAM
# (se toman desde Railway Variables)
# ==========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
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
    "DOGEUSDT"
]

# porcentaje de caída para considerar mercado en miedo
CAIDA_ALERTA = -3   # -3%

# cada cuanto revisar (segundos)
INTERVALO = 300  # 5 minutos


# ==========================
# FUNCION TELEGRAM
# ==========================
def enviar_telegram(mensaje):
    if not BOT_TOKEN or not CHAT_ID:
        print("ERROR: BOT_TOKEN o CHAT_ID no configurados")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": mensaje
    }

    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print("Error enviando mensaje:", e)


# ==========================
# BINANCE API
# ==========================
def obtener_cambio(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    r = requests.get(url, timeout=10)
    data = r.json()
    return float(data["priceChangePercent"])


# ==========================
# INICIO BOT
# ==========================
print("✅ Bot de alerta de CAÍDA iniciado")

# mensaje inicial (para confirmar que funciona)
enviar_telegram("✅ Scanner cripto activo en Railway")

while True:
    try:
        print("Revisando mercado...")
        caidas = []

        for coin in coins:
            cambio = obtener_cambio(coin)
            print(f"{coin}: {cambio}%")

            if cambio <= CAIDA_ALERTA:
                caidas.append((coin, cambio))

        # si 3 o más monedas caen fuerte → alerta
        if len(caidas) >= 3:
            mensaje = "⚠️ ALERTA MERCADO\n\nEl mercado está cayendo fuerte:\n\n"

            for coin, cambio in caidas:
                mensaje += f"{coin}: {round(cambio,2)}%\n"

            mensaje += "\nSentimiento: MIEDO 😨"

            enviar_telegram(mensaje)

        time.sleep(INTERVALO)

    except Exception as e:
        print("Error:", e)
        time.sleep(60)
