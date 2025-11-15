#!/usr/bin/env python3
"""
F4IGV et son amis Chat GPT vous presentent,
Tropo Forecast → DAPNET
Version Windows-friendly avec logs détaillés et message envoyé
Localisation : Rennes
"""

import requests
import json
from datetime import datetime, timezone
from math import exp

# ---------------- CONFIG ----------------
LAT = 48.1173           #les coordonées geographique du lieu duquel vous souhaitez avoir l'indice de propag tropo
LON = -1.6778

DAPNET_URL = "https://hampager.de/api/calls"
DAPNET_USER = "f4abc"               #votre indicatif
DAPNET_PASS = "123456"              #votre mot de passe dapnet
CALLSIGNS = ["f4abc", "f4def"]      #les indicatifs vers lesquels vous voulez envoyer les messages
TX_GROUPS = ["f-53"]                #les groupes d'emmeteur qui enveront le message

LOG_FILE = "tropo.log"
TROPO_MIN_LEVEL = 2.0  # seuil minimal pour envoyer un message
# ----------------------------------------


def log(msg):
    """Log dans la console et dans un fichier UTF-8."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def fetch_weather(lat, lon):
    """Récupère météo actuelle Open-Meteo (current_weather)."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    weather = {
        "t2m": data["current_weather"]["temperature"],
        "wind_speed": data["current_weather"]["windspeed"],
        "wind_dir": data["current_weather"]["winddirection"],
        "pressure": 1013.25,  # approximation si manquante
        "rh": 70  # valeur par défaut si non dispo
    }
    return weather


def refractivity_N(temp_C, pressure_hPa, humidity_percent):
    """Calcule l'indice de réfractivité N (simplifié)."""
    T = temp_C + 273.15
    P = pressure_hPa
    e = humidity_percent / 100 * 6.112 * exp(17.62 * temp_C / (243.12 + temp_C))
    return 77.6 * (P / T) + 3.73e5 * (e / (T * T))


def compute_tropo_index(weather):
    """Calcul de l'indice tropo avec log détaillé."""
    h2m, h100, h925, h850 = 2, 100, 700, 1450
    t2m = weather["t2m"]
    t100 = t2m - 0.65
    t925 = t2m - 5.5
    t850 = t2m - 10
    rh = weather["rh"]
    p2m = weather["pressure"]
    p100 = p2m
    p925 = 925
    p850 = 850

    N2m = refractivity_N(t2m, p2m, rh)
    N100 = refractivity_N(t100, p100, rh)
    N925 = refractivity_N(t925, p925, rh)
    N850 = refractivity_N(t850, p850, rh)

    M2m = N2m + 0.157 * h2m
    M100 = N100 + 0.157 * h100
    M925 = N925 + 0.157 * h925
    M850 = N850 + 0.157 * h850

    grad1 = (M100 - M2m) / (h100 - h2m)
    grad2 = (M925 - M100) / (h925 - h100)
    grad3 = (M850 - M925) / (h850 - h925)

    tropo_index = -(grad1 + grad2 + grad3)

    # Log détaillé
    log(f"Températures approximatives : 2m={t2m}°C, 100m={t100}°C, 925hPa={t925}°C, 850hPa={t850}°C")
    log(f"Réfractivités N : 2m={N2m:.2f}, 100m={N100:.2f}, 925hPa={N925:.2f}, 850hPa={N850:.2f}")
    log(f"Réfractivités Modifiées M : 2m={M2m:.2f}, 100m={M100:.2f}, 925hPa={M925:.2f}, 850hPa={M850:.2f}")
    log(f"Gradients dM/dz : grad1={grad1:.4f}, grad2={grad2:.4f}, grad3={grad3:.4f}")
    log(f"Indice tropo calculé : {tropo_index:.2f}")

    return tropo_index


def alert_level(tindex):
    if tindex < 2:
        return "Faible"
    elif tindex < 4:
        return "Moyenne"
    elif tindex < 6:
        return "Bonne"
    else:
        return "Forte/DX"


def build_message(tindex, weather):
    level = alert_level(tindex)
    return f"Tropo:{tindex:.1f} ({level}) T2m:{weather['t2m']}C RH:{weather['rh']}% P:{weather['pressure']}hPa"


def send_dapnet_message(msg):
    payload = {
        "text": msg,
        "callSignNames": CALLSIGNS,
        "transmitterGroupNames": TX_GROUPS,
        "emergency": False
    }
    headers = {"Content-Type": "application/json"}
    r = requests.post(DAPNET_URL, auth=(DAPNET_USER, DAPNET_PASS),
                      headers=headers, data=json.dumps(payload), timeout=10)
    r.raise_for_status()
    return r


def main():
    log("Récupération météo Open-Meteo…")
    try:
        weather = fetch_weather(LAT, LON)
        log(f"Données météo récupérées : {weather}")
    except Exception as e:
        log(f"[ERROR] Impossible de récupérer météo : {e}")
        return

    tindex = compute_tropo_index(weather)
    level = alert_level(tindex)
    msg = build_message(tindex, weather)
    log(f"Niveau d'alerte : {level}")
    log(f"Message DAPNET proposé : {msg}")

    if tindex >= TROPO_MIN_LEVEL:
        try:
            resp = send_dapnet_message(msg)
            log(f"[OK] Message envoyé à DAPNET : {resp.status_code}")
        except Exception as e:
            log(f"[ERROR] Échec envoi DAPNET : {e}")
    else:
        log("Tropo faible, aucun message envoyé.")


if __name__ == "__main__":
    main()

