# -*- coding: utf-8 -*-
import threading
import time
import traceback
import Svr_Unipi

DI_INDEX = 3            # DI de la cellule 1
RAW_FREE_IS = 1         # Ton Svr_Unipi publie 1 = libre après inversion (cf. INVERT_DI)
POLL_INTERVAL_S = 0.05  # 50 ms
HEARTBEAT_S = 5         # log périodique

class InputWatcher(threading.Thread):
    cellules = {1: 1}   # 1 = libre, 0 = actif
    ready = False
    last_change = 0.0

    def __init__(self, Mode_sans_cellules: int, sim: int):
        super().__init__(name="Etat_Cellule_1_Watcher", daemon=True)
        self.mss = Mode_sans_cellules
        self.sim = sim
        self._cur = 1
        self._last_hb = 0.0

    def _read_cur(self) -> int:
        if self.sim == 0:
            # Lecture DIRECTE du buffer déjà stabilisé par Svr_Unipi
            return int(Svr_Unipi.Svr_Unipi_rec.Inp_3[1])
        else:
            import simulateur
            return int(simulateur.Application.variable1[0])

    def _heartbeat(self, raw_val: int, norm_val: int):
        now = time.time()
        if now - self._last_hb >= HEARTBEAT_S:
            self._last_hb = now

    def run(self):
        try:
            print("[Etat_Cellule_1] Watcher démarré (lecture DI3, source=Svr_Unipi.Inp_3)")
            # Anti faux départ léger côté watcher (Svr_Unipi a déjà son WARMUP interne)
            start = time.time()
            self.cellules[1] = 1
            while time.time() - start < 2.0:
                time.sleep(0.1)

            self.ready = True
            print("[Etat_Cellule_1] ✅ cellules stabilisées, démarrage mesures autorisé")

            if self.mss == 1:
                self.cellules[1] = 1
                print("[Etat_Cellule_1] Mode sans cellules actif → arrêt du watcher")
                return

            while True:
                raw = self._read_cur()
                norm = 1 if raw == RAW_FREE_IS else 0

                if norm != self._cur:
                    self._cur = norm
                    self.cellules[1] = norm
                    self.last_change = time.time()

                self._heartbeat(raw, norm)
                time.sleep(POLL_INTERVAL_S)

        except Exception:
            print("[Etat_Cellule_1][FATAL] Exception dans le watcher :")
            traceback.print_exc()
            self.ready = False
