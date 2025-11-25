# src/gev5/boot/loader.py
"""
Chargement de la configuration système depuis la base Parametres.db.

Cette logique est extraite de legacy/GeV5_Moteur.py pour
avoir une API propre : load_config() -> SystemConfig
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..utils.config import SystemConfig


def _get_parametres(db_path: str) -> Dict[str, str]:
    """
    Lit la table Parametres (nom, valeur) et renvoie un dict {nom: valeur}.
    """
    conn = sqlite3.connect(db_path)
    try:
        c = conn.cursor()
        c.execute("SELECT nom, valeur FROM Parametres")
        rows = c.fetchall()
    finally:
        conn.close()
    return {row[0]: row[1] for row in rows}


def _ensure_db_initialized(db_path: str) -> Dict[str, str]:
    """
    Reprend la logique de GeV5_Moteur.py :
    - tente lecture
    - en cas d'OperationalError, appelle reinit_params et relit
    """
    try:
        return _get_parametres(db_path)
    except sqlite3.OperationalError:
        # On appelle le module legacy pour réinitialiser la base
        from ..legacy import reinit_params  # type: ignore

        # Le module reinit_params initialise Parametres.db.
        # La fonction exacte peut varier, donc on exécute simplement son code.
        if hasattr(reinit_params, "main"):
            reinit_params.main()  # type: ignore
        # Sinon, on suppose que l'import a suffi à créer la table.
        return _get_parametres(db_path)


def _safe_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _safe_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _split_list(value: str) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def load_config(db_path: Optional[str] = None) -> SystemConfig:
    """
    Charge la configuration système complète depuis Parametres.db
    et retourne un objet SystemConfig prêt à l'emploi.
    """

    # Valeur par défaut Raspberry (comme dans GeV5_Moteur.py)
    if db_path is None:
        db_path = "/home/pi/Partage/Base_donnees/Parametres.db"

    # On permet une surcharge en dev si chemin relatif
    db_path = str(Path(db_path))

    raw = _ensure_db_initialized(db_path)

    # --- Conversions de base (copié de GeV5_Moteur.py) ---
    raw["sample_time"] = _safe_float(raw["sample_time"])
    raw["distance_cellules"] = _safe_float(raw["distance_cellules"])
    raw["Mode_sans_cellules"] = _safe_int(raw["Mode_sans_cellules"])
    raw["multiple"] = _safe_float(raw["multiple"])
    raw["seuil2"] = _safe_int(raw["seuil2"])
    raw["low"] = _safe_int(raw["low"])
    raw["high"] = _safe_int(raw["high"])
    raw["camera"] = _safe_int(raw["camera"])
    raw["modbus"] = _safe_int(raw["modbus"])
    raw["eVx"] = _safe_int(raw["eVx"])
    raw["mod_SMS"] = _safe_int(raw["mod_SMS"])
    raw["D1_ON"] = _safe_int(raw["D1_ON"])
    raw["D2_ON"] = _safe_int(raw["D2_ON"])
    raw["D3_ON"] = _safe_int(raw["D3_ON"])
    raw["D4_ON"] = _safe_int(raw["D4_ON"])
    raw["D5_ON"] = _safe_int(raw["D5_ON"])
    raw["D6_ON"] = _safe_int(raw["D6_ON"])
    raw["D7_ON"] = _safe_int(raw["D7_ON"])
    raw["D8_ON"] = _safe_int(raw["D8_ON"])
    raw["D9_ON"] = _safe_int(raw["D9_ON"])
    raw["D10_ON"] = _safe_int(raw["D10_ON"])
    raw["D11_ON"] = _safe_int(raw["D11_ON"])
    raw["D12_ON"] = _safe_int(raw["D12_ON"])

    if raw.get("port") and raw["port"] != "--":
        port: Optional[int] = _safe_int(raw["port"], default=25)
    else:
        port = None

    recipients = _split_list(raw.get("recipients", ""))
    SMS = _split_list(raw.get("SMS", ""))

    # Calcul échéance (identique à GeV5_Moteur.py)
    date_prochaine_visite = datetime.strptime(
        raw["date_prochaine_visite"], "%d/%m/%Y"
    ).date()
    today = datetime.now().date()
    echeance = (date_prochaine_visite - today).days

    pin_1 = _safe_int(raw["PIN_1"])
    pin_2 = _safe_int(raw["PIN_2"])
    pin_3 = _safe_int(raw["PIN_3"])
    pin_4 = _safe_int(raw["PIN_4"])

    sim = _safe_int(raw["SIM"])
    suiv_block = _safe_int(raw.get("suiv_block", "0"))

    Rem_IP = raw["Rem_IP"]
    Rem_IP_2 = raw["Rem_IP_2"]
    base_url = f"http://{Rem_IP}:5002"
    base_url_2 = f"http://{Rem_IP_2}:5002"

    # Construction de l'objet SystemConfig
    cfg = SystemConfig(
        # Infos portique
        nom_portique=raw["Nom_portique"],
        language=raw["language"],

        # Temps / visites
        date_prochaine_visite=date_prochaine_visite,
        echeance=echeance,

        # Comptage / cellules
        sample_time=raw["sample_time"],
        distance_cellules=raw["distance_cellules"],
        mode_sans_cellules=raw["Mode_sans_cellules"],
        multiple=raw["multiple"],
        seuil2=raw["seuil2"],
        low=raw["low"],
        high=raw["high"],
        suiv_block=suiv_block,

        # Activation détecteurs
        D1_ON=raw["D1_ON"],
        D2_ON=raw["D2_ON"],
        D3_ON=raw["D3_ON"],
        D4_ON=raw["D4_ON"],
        D5_ON=raw["D5_ON"],
        D6_ON=raw["D6_ON"],
        D7_ON=raw["D7_ON"],
        D8_ON=raw["D8_ON"],
        D9_ON=raw["D9_ON"],
        D10_ON=raw["D10_ON"],
        D11_ON=raw["D11_ON"],
        D12_ON=raw["D12_ON"],

        # Noms détecteurs
        D1_nom=raw["D1_nom"],
        D2_nom=raw["D2_nom"],
        D3_nom=raw["D3_nom"],
        D4_nom=raw["D4_nom"],
        D5_nom=raw["D5_nom"],
        D6_nom=raw["D6_nom"],
        D7_nom=raw["D7_nom"],
        D8_nom=raw["D8_nom"],
        D9_nom=raw["D9_nom"],
        D10_nom=raw["D10_nom"],
        D11_nom=raw["D11_nom"],
        D12_nom=raw["D12_nom"],

        # IO physiques
        pin_1=pin_1,
        pin_2=pin_2,
        pin_3=pin_3,
        pin_4=pin_4,

        # Simulation
        sim=sim,

        # Caméra / réseau
        camera=raw["camera"],
        RTSP=raw["RTSP"],
        IP=raw["IP"],

        # Réseaux / EVOK
        Rem_IP=Rem_IP,
        Rem_IP_2=Rem_IP_2,
        base_url=base_url,
        base_url_2=base_url_2,

        # Modbus / eVx / SMS
        modbus=raw["modbus"],
        eVx=raw["eVx"],
        mod_SMS=raw["mod_SMS"],
        SMS=SMS,

        # SMTP
        smtp_server=raw["smtp_server"],
        port=port,
        login=raw["login"],
        password=raw["password"],
        sender=raw["sender"],
        recipients=recipients,

        # Divers
        db_path=db_path,
    )

    return cfg
