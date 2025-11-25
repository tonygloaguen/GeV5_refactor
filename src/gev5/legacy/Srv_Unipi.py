#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Svr_Unipi.py — Stable & compatible
- DI 3/4/5 via WebSocket (input/di) + REST fallback (bulk puis /rest/di/{c})
- AI via WebSocket EVOK (optionnel : si websocket-client absent, on ignore)
- États compatibles: Inp_3[1], Inp_4[1], Inp_5[1], Ai_1[1], Ai_2[1]
- Ajouts:
  * INVERT_DI par circuit (3/4/5) pour inversion logique si besoin
  * WARMUP_S pour ignorer les basculements pendant les premières secondes
  * STABLE_MS pour débounce/anti-rebond avant publication
"""

import json
import time
import threading
import urllib.request
from typing import Optional

# -------------------- Config --------------------
EVOK_WS_URL     = "ws://127.0.0.1:8080/ws"
REST_BASE       = "http://127.0.0.1:8080"
REST_DI_BULK    = (f"{REST_BASE}/rest/di", f"{REST_BASE}/rest/input", f"{REST_BASE}/rest/all")
REST_DI_ONE     = (f"{REST_BASE}/rest/di/{{c}}", f"{REST_BASE}/rest/input/{{c}}")

POLL_PERIOD_S   = 0.2   # 200 ms : assez rapide tout en restant léger
PING_INTERVAL   = 30
PING_TIMEOUT    = 5
RECONNECT_DELAY = 1.0

# Circuits suivis (d'après evok.conf)
TRACKED_DI = (3, 4, 5)

# Debug léger au démarrage
DEBUG_BOOT_PRINTS = 8

# --- Options I/O ---
# Mets à True pour inverser un circuit donné (3/4/5) sans toucher au câblage.
INVERT_DI = {3: False, 4: False, 5: False}

# Ignore les basculements pendant WARMUP_S secondes après démarrage (anti-front fantôme)
WARMUP_S = 5

# Nécessite STABLE_MS ms de stabilité avant de publier une nouvelle valeur (anti-rebond)
STABLE_MS = 100

# -------------------- Déps WS optionnelles --------------------
try:
    import websocket  # pip install websocket-client
    _WS_ENABLED = True
except Exception:
    websocket = None
    _WS_ENABLED = False


# -------------------- Utils --------------------
def _coerce01(v) -> int:
    """Normalise valeur EVOK en 0/1 (0 = libre, 1 = obstrué/panne)."""
    try:
        if isinstance(v, bool):
            return 0 if v else 1
        if isinstance(v, (int, float)):
            return 0 if int(v) != 0 else 1
        s = str(v).strip().lower()
        if s in ("1", "true", "on", "high"):
            return 0
        if s in ("0", "false", "off", "low"):
            return 1
    except Exception:
        pass
    return 1



def _rest_get_one_di(c: int, timeout=0.4) -> Optional[int]:
    """Lit /rest/di/{c} (ou /rest/input/{c}) et retourne 0/1 ou None si échec."""
    headers = {"Accept": "application/json"}
    for tpl in REST_DI_ONE:
        url = tpl.format(c=c)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as r:
                data = json.loads(r.read().decode("utf-8", errors="ignore"))
                return _coerce01(data.get("value", 0))
        except Exception:
            continue
    return None


def _rest_get_all_di(timeout=0.6):
    """
    Essaie d'abord les endpoints bulk (/rest/di, /rest/input, /rest/all).
    Si rien, bascule en /rest/di/{c} pour chaque circuit suivi.
    Retourne {circuit:int -> 0/1}.
    """
    headers = {"Accept": "application/json"}

    # 1) Bulk
    for url in REST_DI_BULK:
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as r:
                raw = r.read().decode("utf-8", errors="ignore")
                data = json.loads(raw)
                frames = data if isinstance(data, list) else [data]
                mp = {}
                for it in frames:
                    if not isinstance(it, dict):
                        continue
                    dev = str(it.get("dev", "")).lower()
                    if dev not in ("input", "di"):
                        continue
                    try:
                        c = int(str(it.get("circuit", "")).strip())
                    except Exception:
                        continue
                    mp[c] = _coerce01(it.get("value", 0))
                if mp:
                    return mp
        except Exception:
            continue

    # 2) Per-circuit fallback
    mp = {}
    for c in TRACKED_DI:
        v = _rest_get_one_di(c)
        if v is not None:
            mp[c] = v
    return mp


class Svr_Unipi_rec(threading.Thread):
    """
    Thread WS (AI + DI). DI aussi polled via REST dans un thread séparé.
    Expose des listes [0, val] pour compatibilité avec le code existant.
    """
    Inp_3 = [0, 0]
    Inp_4 = [0, 0]
    Inp_5 = [0, 0]
    Ai_1  = [0.0, 0.0]
    Ai_2  = [0.0, 0.0]

    _instance_lock = threading.Lock()
    _instance = None

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        super().__init__(name="Svr_Unipi_rec", daemon=True)
        self._initialized = True
        self._stop = threading.Event()

        # WebSocket si dispo
        self._ws = None
        self._ws_lock = threading.Lock()
        self._ws_alive = False

        # État DI pour debounce & warm-up
        self._boot_ts = time.time()
        self._di_last = {c: None for c in TRACKED_DI}           # dernière valeur vue (immédiate)
        self._di_last_change = {c: 0.0 for c in TRACKED_DI}      # timestamp dernier changement
        self._di_stable = {c: None for c in TRACKED_DI}          # dernière valeur publiée (stable)

        # Lance le poller DI (REST)
        self._di_thread = threading.Thread(target=self._poll_di_rest, name="DI_REST", daemon=True)
        self._di_thread.start()

    # ------------- DI via REST -------------
    def _poll_di_rest(self):
        shown = 0
        while not self._stop.is_set():
            if self._ws_alive:
                time.sleep(1.0)
                continue

            mp = _rest_get_all_di(timeout=0.5)

            # Debug court au boot
            if shown < DEBUG_BOOT_PRINTS:
                print(f"[DI_REST] mp={mp}")
                shown += 1

            # Met à jour uniquement ce qu'on suit, avec inversion + debounce + warmup
            now = time.time()
            for c in TRACKED_DI:
                v = mp.get(c)
                if v is None:
                    continue
                if INVERT_DI.get(c, False):
                    v = 1 - v

                # Première init: fixe last/stable dès la première valeur
                if self._di_last[c] is None:
                    self._di_last[c] = v
                    self._di_last_change[c] = now
                    self._di_stable[c] = v  # on publie immédiatement la première valeur
                    if c == 3: Svr_Unipi_rec.Inp_3[1] = v
                    elif c == 4: Svr_Unipi_rec.Inp_4[1] = v
                    elif c == 5: Svr_Unipi_rec.Inp_5[1] = v
                    continue

                # Détection de changement brut
                if self._di_last[c] != v:
                    self._di_last[c] = v
                    self._di_last_change[c] = now

                # Conditions de publication
                stable = (now - self._di_last_change[c]) * 1000.0 >= STABLE_MS
                warmed = (now - self._boot_ts) >= WARMUP_S

                if stable and warmed and self._di_stable[c] != v:
                    self._di_stable[c] = v
                    if c == 3: Svr_Unipi_rec.Inp_3[1] = v
                    elif c == 4: Svr_Unipi_rec.Inp_4[1] = v
                    elif c == 5: Svr_Unipi_rec.Inp_5[1] = v

            time.sleep(POLL_PERIOD_S)

    # ------------- AI/DI via WebSocket -------------
    def _build_ws(self):
        if not _WS_ENABLED:
            return
        self._ws = websocket.WebSocketApp(
            EVOK_WS_URL,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

    def _send_json(self, payload: dict):
        if not _WS_ENABLED:
            return
        try:
            with self._ws_lock:
                if self._ws:
                    self._ws.send(json.dumps(payload))
        except Exception as e:
            print(f"[Svr_Unipi] send error: {e}")

    def _on_open(self, ws):
        # On s’abonne à tout : AI + DI (input/di) et snapshot
        self._send_json({"cmd": "subscribe", "dev": "all"})
        self._send_json({"cmd": "subscribe", "dev": "input"})
        self._send_json({"cmd": "subscribe", "dev": "di"})
        self._send_json({"cmd": "subscribe", "dev": "ai"})
        self._send_json({"cmd": "all"})
        self._ws_alive = True
        print("[Svr_Unipi] WS ouvert (AI+DI)")

    def _on_message(self, ws, message: str):
        try:
            data = json.loads(message)
        except Exception:
            return
        frames = []
        if isinstance(data, dict):
            frames = data.get("data") if isinstance(data.get("data"), list) else [data]
        elif isinstance(data, list):
            frames = data

        for it in frames or []:
            if not isinstance(it, dict):
                continue
            dev = str(it.get("dev", "")).lower()
            if dev in ("ai", "ain", "analog", "analoginput"):
                self._ingest_ai(it)
            elif dev in ("input", "di"):
                self._ingest_di(it)

    def _ingest_ai(self, frame: dict):
        c = str(frame.get("circuit", "")).strip()
        try:
            v = float(frame.get("value"))
        except Exception:
            return
        if c == "1": Svr_Unipi_rec.Ai_1[1] = v
        elif c == "2": Svr_Unipi_rec.Ai_2[1] = v

    def _ingest_di(self, frame: dict):
        c = str(frame.get("circuit", "")).strip()
        v = _coerce01(frame.get("value", 0))
        if INVERT_DI.get(int(c), False):
            v = 1 - v

        now = time.time()
        ci = int(c) if c.isdigit() else None
        if ci in TRACKED_DI:
            # Débounce + warmup appliqués aussi au flux WS
            if self._di_last[ci] is None:
                self._di_last[ci] = v
                self._di_last_change[ci] = now
                self._di_stable[ci] = v
                if ci == 3: Svr_Unipi_rec.Inp_3[1] = v
                elif ci == 4: Svr_Unipi_rec.Inp_4[1] = v
                elif ci == 5: Svr_Unipi_rec.Inp_5[1] = v
                return

            if self._di_last[ci] != v:
                self._di_last[ci] = v
                self._di_last_change[ci] = now

            stable = (now - self._di_last_change[ci]) * 1000.0 >= STABLE_MS
            warmed = (now - self._boot_ts) >= WARMUP_S
            if stable and warmed and self._di_stable[ci] != v:
                self._di_stable[ci] = v
                if ci == 3: Svr_Unipi_rec.Inp_3[1] = v
                elif ci == 4: Svr_Unipi_rec.Inp_4[1] = v
                elif ci == 5: Svr_Unipi_rec.Inp_5[1] = v

    def _on_error(self, ws, err):
        self._ws_alive = False
        print(f"[Svr_Unipi] WS erreur: {err}")

    def _on_close(self, ws, status, msg):
        self._ws_alive = False
        print(f"[Svr_Unipi] WS fermé: {status} {msg}")

    # ------------- Thread principal -------------
    def run(self):
        if not _WS_ENABLED:
            # Pas de websocket-client installé : on ne fait pas d'AI/DI en WS, mais on reste vivant.
            while not self._stop.is_set():
                time.sleep(0.5)
            print("[Svr_Unipi] Thread arrêté (WS désactivé)")
            return

        # Avec websocket-client : on écoute AI+DI
        while not self._stop.is_set():
            self._build_ws()
            try:
                self._ws.run_forever(
                    ping_interval=PING_INTERVAL,
                    ping_timeout=PING_TIMEOUT,
                )
            except Exception as e:
                print(f"[Svr_Unipi] run_forever exception: {e}")

            if self._stop.is_set():
                break
            time.sleep(RECONNECT_DELAY)

        print("[Svr_Unipi] Thread arrêté")

    def stop(self, wait: bool = True):
        self._stop.set()
        if _WS_ENABLED:
            with self._ws_lock:
                try:
                    if self._ws:
                        self._ws.close()
                except Exception:
                    pass
        if wait and self.is_alive():
            self.join(timeout=2.0)


# --------- API module-level --------- #
_srv_thread: Optional[Svr_Unipi_rec] = None
_srv_lock = threading.Lock()

def demarrage_Srv_Unipi():
    """Démarre le listener si pas déjà lancé."""
    global _srv_thread
    with _srv_lock:
        if _srv_thread is None or not _srv_thread.is_alive():
            _srv_thread = Svr_Unipi_rec()
            _srv_thread.start()
            time.sleep(0.2)
    return _srv_thread

def arret_Srv_Unipi():
    """Arrête proprement le listener si lancé."""
    global _srv_thread
    with _srv_lock:
        if _srv_thread is not None:
            _srv_thread.stop(wait=True)
            _srv_thread = None


# --------- TEST DIRECT --------- #
# if __name__ == "__main__":
#     demarrage_Srv_Unipi()
#     try:
#         while True:
#             print(
#                 f"DI3={Svr_Unipi_rec.Inp_3[1]}  DI4={Svr_Unipi_rec.Inp_4[1]}  DI5={Svr_Unipi_rec.Inp_5[1]}  "
#                 f"|  AI1={Svr_Unipi_rec.Ai_1[1]:.4f}  AI2={Svr_Unipi_rec.Ai_2[1]:.4f}"
#             )
#             time.sleep(0.5)
#     except KeyboardInterrupt:
#         arret_Srv_Unipi()
#         print("\\n🛑 Arrêt du listener.")
