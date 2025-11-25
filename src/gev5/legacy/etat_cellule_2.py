# -*- coding: utf-8 -*-
import threading
import time
import traceback
import Svr_Unipi

DI_INDEX = 4
RAW_FREE_IS = 1
POLL_INTERVAL_S = 0.05
HEARTBEAT_S = 5

class InputWatcher(threading.Thread):
    cellules = {2: 1}
    ready = False
    last_change = 0.0

    def __init__(self, Mode_sans_cellules: int, sim: int):
        super().__init__(name="Etat_Cellule_2_Watcher", daemon=True)
        self.mss = Mode_sans_cellules
        self.sim = sim
        self._cur = 1
        self._last_hb = 0.0

    def _read_cur(self) -> int:
        if self.sim == 0:
            return int(Svr_Unipi.Svr_Unipi_rec.Inp_4[1])
        else:
            import simulateur
            return int(simulateur.Application.variable2[0])

    def _heartbeat(self, raw_val: int, norm_val: int):
        now = time.time()
        if now - self._last_hb >= HEARTBEAT_S:
            self._last_hb = now

    def run(self):
        try:
            print("[Etat_Cellule_2] Watcher démarré (lecture DI4, source=Svr_Unipi.Inp_4)")
            start = time.time()
            self.cellules[2] = 1
            while time.time() - start < 2.0:
                time.sleep(0.1)

            self.ready = True
            print("[Etat_Cellule_2] ✅ cellules stabilisées, démarrage mesures autorisé")

            if self.mss == 1:
                self.cellules[2] = 1
                print("[Etat_Cellule_2] Mode sans cellules actif → arrêt du watcher")
                return

            while True:
                raw = self._read_cur()
                norm = 1 if raw == RAW_FREE_IS else 0

                if norm != self._cur:
                    self._cur = norm
                    self.cellules[2] = norm
                    self.last_change = time.time()

                self._heartbeat(raw, norm)
                time.sleep(POLL_INTERVAL_S)

        except Exception:
            print("[Etat_Cellule_2][FATAL] Exception dans le watcher :")
            traceback.print_exc()
            self.ready = False
