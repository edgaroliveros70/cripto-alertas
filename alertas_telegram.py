import os
import sys
import time

import requests
import yfinance as yf

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

ACTIVOS = {
    "Bitcoin": "BTC-USD",
    "Oro": "GC=F",
    "Nasdaq": "^IXIC",
}
UMBRAL_PCT = float(os.environ.get("UMBRAL_PCT", "1.0"))
INTERVALO_SEG = int(os.environ.get("INTERVALO_SEG", "300"))


def enviar(texto):
    if not TOKEN or not CHAT_ID:
        print("[sin token/chat_id] " + texto)
        return
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": texto},
        timeout=15,
    )
    if not r.ok:
        print("Error Telegram:", r.status_code, r.text)


def obtener_chat_id():
    r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", timeout=15).json()
    for u in r.get("result", []):
        chat = (u.get("message") or {}).get("chat")
        if chat:
            print("chat_id:", chat["id"], "-", chat.get("first_name") or chat.get("title"))
    if not r.get("result"):
        print("No hay mensajes. Escríbele algo a tu bot en Telegram y vuelve a correr esto.")


def precio(simbolo):
    return float(yf.Ticker(simbolo).fast_info["last_price"])


def main():
    referencia = {}
    resumen = []
    for nombre, simbolo in ACTIVOS.items():
        referencia[nombre] = precio(simbolo)
        resumen.append(f"{nombre}: {referencia[nombre]:,.2f}")
    enviar("Bot de alertas iniciado\n" + "\n".join(resumen))

    while True:
        time.sleep(INTERVALO_SEG)
        for nombre, simbolo in ACTIVOS.items():
            try:
                actual = precio(simbolo)
            except Exception as e:
                print(f"Error leyendo {nombre}: {e}")
                continue
            cambio = (actual - referencia[nombre]) / referencia[nombre] * 100
            if abs(cambio) >= UMBRAL_PCT:
                flecha = "SUBE" if cambio > 0 else "BAJA"
                enviar(f"{nombre} {flecha} {cambio:+.2f}%\nAntes: {referencia[nombre]:,.2f}\nAhora: {actual:,.2f}")
                referencia[nombre] = actual


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "chatid":
        obtener_chat_id()
    else:
        main()
