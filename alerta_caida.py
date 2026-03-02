import requests
import time

# ==========================
# CONFIGURACION TELEGRAM
# ==========================
TOKEN = "8669093219:AAHx_ytsvsCFeDc6Zf-BFcw-taGtjjlnkHc"
CHAT_ID = "6517297394"

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


def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": mensaje
    }
    requests.post(url, data=data)


def obtener_cambio(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    r = requests.get(url)
    data = r.json()
    return float(data["priceChangePercent"])


print("Bot de alerta de CAÍDA iniciado...")

while True:
    try:
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