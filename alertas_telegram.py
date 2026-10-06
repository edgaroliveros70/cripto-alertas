import os
import requests
import yfinance as yf

# Reemplaza o pasa estos valores como variables de entorno
TELEGRAM_TOKEN = os.getenv("8760108023:AAGGucW-ilGgXIU6A68mA_K1MTekl0yc2Xs")
TELEGRAM_CHAT_ID = os.getenv("944323495")


def obtener_precios():
    tickers = {"Bitcoin": "BTC-USD", "Oro": "GC=F", "Nasdaq": "^IXIC"}

    mensaje = "📊 *Reporte de Precios - Cripto Alertas*\n\n"

    for nombre, ticker in tickers.items():
        data = yf.Ticker(ticker)
        info = data.fast_info
        precio_actual = info.last_price
        precio_previo = info.previous_close

        variacion = ((precio_actual - precio_previo) / precio_previo) * 100
        signo = "+" if variacion >= 0 else ""

        mensaje += (
            f"• *{nombre}:* ${precio_actual:,.2f} ({signo}{variacion:.2f}%)\n"
        )

    return mensaje


def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    return response.json()


if __name__ == "__main__":
    texto = obtener_precios()
    enviar_telegram(texto)
