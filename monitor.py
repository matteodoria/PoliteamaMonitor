
import os
import json
import requests

from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.politeamagreco.it/scheda.asp?id=1151"
TARGET = "frase inesistente"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

STATE_FILE = Path(__file__).parent / "state.json"


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())

    return {"available": False}


def save_state(available):
    STATE_FILE.write_text(
        json.dumps({"available": available}, indent=4)
    )


def send_notification(message):
    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": message},
        timeout=15
    )
    response.raise_for_status()


def check_website():
    response = requests.get(URL, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    text = text.replace("\u200b", "")
    text = " ".join(text.lower().split())

    if "filippo caccamo" not in text:
        raise RuntimeError("Contenuto della pagina non valido")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    previous_state = load_state()["available"]
    available = TARGET not in text

    if not available:
        print(f"[{timestamp}] Biglietti non disponibili.")

    elif not previous_state:
        send_notification(
            "🎟️ POSSIBILE APERTURA DELLE VENDITE!\n\n"
            "Filippo Caccamo - Fuori di tela\n"
            "📅 18 marzo 2027, ore 21:00\n"
            "📍 Teatro Politeama Greco, Lecce\n\n"
            f"{URL}"
        )
        print(f"[{timestamp}] Notifica inviata!")

    else:
        print(f"[{timestamp}] Notifica già inviata.")

    save_state(available)


if __name__ == "__main__":
    check_website()
